import uuid
from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    points = models.IntegerField(default=0)

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
    mode = models.CharField(max_length=20, default='hard')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.id} - {self.status}"
