"""
Management command: rebuild_monthly_points

Reconciles UserPoints aggregates against the PointsEvent audit log.
Use for disaster recovery or after manual DB interventions.

Usage:
    python manage.py rebuild_monthly_points --month=2026-02
    python manage.py rebuild_monthly_points  # defaults to current month
"""

from django.core.management.base import BaseCommand
from django.db import transaction
from django.db.models import Sum
from django.utils import timezone

from hardle.models import UserPoints, PointsEvent


class Command(BaseCommand):
    help = "Rebuild UserPoints for a given month from PointsEvent audit log."

    def add_arguments(self, parser):
        parser.add_argument(
            "--month",
            type=str,
            default=None,
            help="Month to reconcile in YYYY-MM format. Defaults to current month.",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Show what would change without modifying data.",
        )

    def handle(self, *args, **options):
        month = options["month"] or timezone.now().strftime("%Y-%m")
        dry_run = options["dry_run"]

        self.stdout.write(f"\n{'=' * 60}")
        self.stdout.write(f"  REBUILD MONTHLY POINTS — {month}")
        self.stdout.write(f"  Mode: {'DRY RUN' if dry_run else 'LIVE'}")
        self.stdout.write(f"{'=' * 60}\n")

        # Step 1: Compute correct totals from PointsEvent
        # Filter events by month (created_at falls within the month)
        year, mo = month.split("-")
        event_totals = (
            PointsEvent.objects
            .filter(created_at__year=int(year), created_at__month=int(mo))
            .values("user_id")
            .annotate(correct_total=Sum("points"))
        )

        correct_map = {row["user_id"]: row["correct_total"] for row in event_totals}

        # Step 2: Read current UserPoints rows for this month
        current_rows = UserPoints.objects.filter(month=month)
        current_map = {row.user_id: row.total_points for row in current_rows}

        # Step 3: Compute diffs
        all_user_ids = set(correct_map.keys()) | set(current_map.keys())

        mismatches = []
        missing_rows = []
        orphan_rows = []

        for uid in all_user_ids:
            correct = correct_map.get(uid, 0)
            current = current_map.get(uid, None)

            if current is None:
                # Event exists but no UserPoints row
                missing_rows.append((uid, correct))
            elif uid not in correct_map:
                # UserPoints row exists but no events (orphan)
                orphan_rows.append((uid, current))
            elif current != correct:
                mismatches.append((uid, current, correct))

        # Step 4: Report
        self.stdout.write(f"  Users with events this month:   {len(correct_map)}")
        self.stdout.write(f"  Current UserPoints rows:        {len(current_map)}")
        self.stdout.write(f"  Mismatches (wrong total):       {len(mismatches)}")
        self.stdout.write(f"  Missing rows (need insert):     {len(missing_rows)}")
        self.stdout.write(f"  Orphan rows (no events):        {len(orphan_rows)}")
        self.stdout.write("")

        if mismatches:
            self.stdout.write("  MISMATCHES:")
            for uid, current, correct in mismatches[:20]:
                self.stdout.write(f"    User {uid}: {current} → {correct} (delta: {correct - current})")
            if len(mismatches) > 20:
                self.stdout.write(f"    ... and {len(mismatches) - 20} more")

        if missing_rows:
            self.stdout.write("  MISSING ROWS:")
            for uid, correct in missing_rows[:10]:
                self.stdout.write(f"    User {uid}: should be {correct}")
            if len(missing_rows) > 10:
                self.stdout.write(f"    ... and {len(missing_rows) - 10} more")

        if orphan_rows:
            self.stdout.write("  ORPHAN ROWS (will be zeroed):")
            for uid, current in orphan_rows[:10]:
                self.stdout.write(f"    User {uid}: currently {current}, no events found")

        total_fixes = len(mismatches) + len(missing_rows) + len(orphan_rows)

        if total_fixes == 0:
            self.stdout.write(self.style.SUCCESS("\n  [OK] No discrepancies found. UserPoints is consistent.\n"))
            return

        if dry_run:
            self.stdout.write(self.style.WARNING(f"\n  DRY RUN: {total_fixes} fixes would be applied. Re-run without --dry-run to execute.\n"))
            return

        # Step 5: Apply fixes inside a transaction
        with transaction.atomic():
            # Fix mismatches
            for uid, _current, correct in mismatches:
                UserPoints.objects.filter(user_id=uid, month=month).update(total_points=correct)

            # Insert missing rows
            for uid, correct in missing_rows:
                UserPoints.objects.create(user_id=uid, month=month, total_points=correct)

            # Zero out orphans (don't delete — preserve the row for auditability)
            for uid, _current in orphan_rows:
                UserPoints.objects.filter(user_id=uid, month=month).update(total_points=0)

        self.stdout.write(self.style.SUCCESS(
            f"\n  [OK] Reconciliation complete."
            f"\n    Mismatches corrected: {len(mismatches)}"
            f"\n    Missing rows created: {len(missing_rows)}"
            f"\n    Orphan rows zeroed:   {len(orphan_rows)}"
            f"\n    Total fixes applied:  {total_fixes}\n"
        ))
