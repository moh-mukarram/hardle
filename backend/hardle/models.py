import uuid
from django.db import models

class GameStatus(models.TextChoices):
    IN_PROGRESS = 'IN_PROGRESS', 'In Progress'
    WIN = 'WIN', 'Win'
    LOSE = 'LOSE', 'Lose'

class GameSession(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    # For v1 foundational, we might not have a User model yet, but we track session/device via ID
    # If auth was required, we'd add ForeignKey to User. For now, assume anonymous or simple.
    target_word = models.CharField(max_length=5)  # SECRET
    guesses = models.JSONField(default=list)  # List of {word: str, colors: list[int]}
    status = models.CharField(
        max_length=20,
        choices=GameStatus.choices,
        default=GameStatus.IN_PROGRESS
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.id} - {self.status}"
