import uuid
from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    points = models.IntegerField(default=0)
    is_guest = models.BooleanField(default=False)

    def __str__(self):
        return self.user.username


class GameStatus(models.TextChoices):
    IN_PROGRESS = 'IN_PROGRESS', 'In Progress'
    WIN = 'WIN', 'Win'
    LOSE = 'LOSE', 'Lose'

class GameSession(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    # Optional link to user if authenticated
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    
    target_word = models.CharField(max_length=5)  # SECRET
    guesses = models.JSONField(default=list)  # List of {word: str, colors: list[int]}
    status = models.CharField(
        max_length=20,
        choices=GameStatus.choices,
        default=GameStatus.IN_PROGRESS
    )
    mode = models.CharField(max_length=20, default='daily')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=["user", "created_at"]),
        ]

    def __str__(self):
        return f"{self.id} - {self.status}"


class UserPoints(models.Model):
    """Per-user, per-month points aggregate. One row per user per month."""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_points')
    total_points = models.IntegerField(default=0)
    month = models.CharField(max_length=7, db_index=True)  # "YYYY-MM"
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', 'month')
        indexes = [
            models.Index(fields=["month", "-total_points"]),
        ]

    def __str__(self):
        return f"{self.user.username} — {self.month}: {self.total_points}pts"


class PointsEvent(models.Model):
    """Append-only audit log. Every point change is recorded here."""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='points_events')
    source = models.CharField(max_length=50)  # "hardle_daily", "future_game", etc.
    points = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=['user', 'created_at']),
        ]

    def __str__(self):
        return f"{self.user.username} +{self.points} ({self.source})"
