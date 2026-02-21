"""
PointsService — the ONLY authority for points mutations.

Rules:
- award_points is idempotent for "daily" modes (one award per user+source+day)
- award_points allows repeated wins for all other modes
- award_points always creates a PointsEvent
- total_points on UserPoints is updated atomically
- No other code may modify points
- Leaderboard ALWAYS resolves names from User (not UserProfile)

Usage:
    from hardle.points_service import PointsService
    PointsService.award_points(user, "hardle_daily", 10)
"""

from django.db import transaction
from django.db.models import F
from django.utils import timezone

from .models import UserPoints, PointsEvent
from .ranks import get_rank


class PointsService:
    """Single service that owns all points reads and writes."""

    @staticmethod
    def award_points(user, source: str, points: int) -> bool:
        """
        Award points to a user for a given source.

        Idempotency: If the same user+source already has an event TODAY,
        this is a no-op and returns False.

        Returns True if points were awarded, False if skipped (duplicate).
        """
        today = timezone.now().date()
        current_month = today.strftime("%Y-%m")

        with transaction.atomic():
            # Idempotency check: only enforced for "daily" mode.
            # Other modes (hard, extreme, etc.) allow repeated wins.
            #
            # Sources may include a session UUID suffix (e.g. "hardle_daily:uuid").
            # We extract the prefix before ":" and check if ANY event with a
            # source starting with that prefix was already recorded today.
            if ':' in source:
                prefix = source.split(':')[0]  # "hardle_daily:uuid" -> "hardle_daily"
                
                # Lock rows matching criteria to prevent parallel race conditions
                already_awarded = PointsEvent.objects.select_for_update().filter(
                    user=user,
                    source__startswith=prefix,
                    created_at__date=today,
                ).exists()

                if already_awarded:
                    return 0
            # 1. Create the immutable event record
            PointsEvent.objects.create(
                user=user,
                source=source,
                points=points,
            )

            # 2. Upsert UserPoints for this month, atomically add points
            user_points, created = UserPoints.objects.get_or_create(
                user=user,
                month=current_month,
                defaults={"total_points": points},
            )
            if not created:
                # Use F() for atomic increment — no race conditions
                UserPoints.objects.filter(
                    pk=user_points.pk
                ).update(
                    total_points=F("total_points") + points,
                )

            # 3. Also update the legacy UserProfile.points for backward compat
            if hasattr(user, "profile"):
                from .models import UserProfile
                UserProfile.objects.filter(
                    pk=user.profile.pk
                ).update(
                    points=F("points") + points,
                )

        return points

    @staticmethod
    def get_user_points(user, month: str = None) -> int:
        """
        Get total points for a user in a given month.
        Defaults to current month.
        """
        if month is None:
            month = timezone.now().strftime("%Y-%m")

        try:
            user_points = UserPoints.objects.get(user=user, month=month)
            return user_points.total_points
        except UserPoints.DoesNotExist:
            return 0

    @staticmethod
    def get_leaderboard(month: str = None, limit: int = 100) -> list:
        """
        Return the leaderboard for a given month.
        Each entry: {username, total_points, rank}
        Sorted by total_points DESC.
        """
        if month is None:
            month = timezone.now().strftime("%Y-%m")

        entries = (
            UserPoints.objects
            .filter(month=month)
            .select_related("user")
            .order_by("-total_points")[:limit]
        )

        results = []
        for entry in entries:
            # Username Resolution Logic
            # 1. Use username if available
            # 2. Fallback to email
            # 3. Fallback to "Unknown"
            display_name = entry.user.username
            if not display_name:
                display_name = entry.user.email
            if not display_name:
                display_name = "Unknown"

            results.append({
                "username": display_name,
                "points": entry.total_points,
                "rank": get_rank(entry.total_points),
            })
            
        return results
