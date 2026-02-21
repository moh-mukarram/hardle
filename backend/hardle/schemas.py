from ninja import Schema
from typing import List, Optional
from uuid import UUID

class GuessRequest(Schema):
    guess: str

class GuessDetail(Schema):
    word: str
    colors: List[int]

class GameSessionSchema(Schema):
    id: UUID
    status: str
    mode: str = 'hard'
    guesses: List[GuessDetail]
    target_word: Optional[str] = None
    results: Optional[dict] = None  # outcome, points_delta, ranks, etc.

# Auth Schemas
class SignupRequest(Schema):
    username: str
    email: str
    password: str

class LoginRequest(Schema):
    email: str
    password: str

class UserSchema(Schema):
    username: str
    email: str
    points: int = 0
    rank: str = "Bronze"

class LeaderboardEntry(Schema):
    username: str
    points: int
    rank: str = "Bronze"
