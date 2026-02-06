from ninja import Schema
from typing import List
from uuid import UUID

class GuessRequest(Schema):
    guess: str

class GuessDetail(Schema):
    word: str
    colors: List[int]

class GameSessionSchema(Schema):
    id: UUID
    status: str
    guesses: List[GuessDetail]
    # target_word is intentionally OMITTED
