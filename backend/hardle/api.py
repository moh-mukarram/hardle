from ninja import NinjaAPI
from django.shortcuts import get_object_or_404
from .models import GameSession
from .schemas import GameSessionSchema, GuessRequest
from .services import GameService

api = NinjaAPI(title="Hardle v1.0 API")

@api.get("/game/state", response=GameSessionSchema)
def get_game_state(request, session_id: str = None):
    # For v1, generic session handling. 
    # If session_id provided in query param, try to load.
    # If not found or not provided, create new.
    # In a real app, this would use cookies or headers.
    
    session = None
    if session_id:
        session = GameService.get_session(session_id)
    
    if not session:
        session = GameService.create_session()
    
    return session

@api.post("/game/guess", response={200: GameSessionSchema, 400: dict})
def submit_guess(request, payload: GuessRequest, session_id: str):
    # session_id required for guessing
    try:
        session = GameService.process_guess(session_id, payload.guess)
        return session
    except ValueError as e:
        return 400, {"message": str(e)}

@api.post("/game/reset", response=GameSessionSchema)
def reset_game(request):
    # Always creates a new session
    session = GameService.create_session()
    return session
