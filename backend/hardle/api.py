from ninja import NinjaAPI, Router, Query
from django.shortcuts import get_object_or_404
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.db import IntegrityError
from django.utils import timezone
from .models import GameSession, UserProfile
from .schemas import (
    GameSessionSchema, GuessRequest, 
    SignupRequest, LoginRequest, UserSchema, LeaderboardEntry
)
from .services import GameService
from .points_service import PointsService
from .ranks import get_rank
from typing import List, Optional

def _get_daily_results(request, session, guess_used=None):
    """Helper to construct the results object for Daily Mode game end."""
    if str(session.status) not in ['WIN', 'LOSE'] or getattr(session, 'mode', 'hard') != 'daily':
        return None
        
    points = GameService.calculate_daily_score(session)
    source = f"hardle_daily"
    
    # Ranks and Points (for authenticated users)
    rank_after = "N/A"
    points_delta = 0
    
    if request.user.is_authenticated:
        # Don't award points here (get_game_state is read-only), 
        # just fetch current stats. award_points is in submit_guess.
        current_points = PointsService.get_user_points(request.user)
        rank_after = get_rank(current_points)
        points_delta = getattr(session, '_awarded_points', points)
    
    # Count colors for summary
    total_green = 0
    total_yellow = 0
    for g in session.guesses:
        cols = g.get("colors", [])
        total_green += cols.count(2)  # COLOR_GREEN
        total_yellow += cols.count(1) # COLOR_YELLOW

    outcome = "SESSION_EXPIRED" if guess_used == "__TIMEOUT__" else str(session.status)
    
    return {
        "outcome": outcome,
        "solution": session.target_word,
        "greens_count": total_green,
        "yellows_count": total_yellow,
        "points_delta": points_delta,
        "rank_current": rank_after, 
        "rank_after": rank_after
    }

api = NinjaAPI(title="Hardle v1.0 API")

# --- Game Router ---
@api.get("/game/state", response=GameSessionSchema)
def get_game_state(request, session_id: str = None, mode: str = 'hard'):
    # Session loading logic similar to previous version
    session = None
    if session_id:
        session = GameService.get_session(session_id)
    
    if not session:
        # IDEMPOTENCY CHECK FOR DAILY MODE
        if mode == 'daily' and request.user.is_authenticated:
            today = timezone.now().date()
            existing_daily = GameSession.objects.filter(
                user=request.user,
                mode='daily',
                created_at__date=today
            ).first()
            if existing_daily:
                session = existing_daily
        
        # Create new if still no session
        if not session:
            session = GameService.create_session(mode=mode)
            # If user is authenticated, link session
            if request.user.is_authenticated:
                session.user = request.user
                session.save()
            
    # Expose target_word only if game is over
    target_word = session.target_word if session.status in ['WIN', 'LOSE'] else None

    # explicit construction for safety
    response_data = {
        "id": session.id,
        "status": session.status,
        "guesses": session.guesses,
        "mode": session.mode if hasattr(session, 'mode') else 'hard',
        "target_word": target_word,
        "results": _get_daily_results(request, session)
    }
            
    return response_data

@api.post("/game/guess", response={200: GameSessionSchema, 400: dict})
def submit_guess(request, payload: GuessRequest, session_id: str):
    try:
        session = GameService.process_guess(session_id, payload.guess)
        results = None
        if request.user.is_authenticated:
            # Ensure session is linked
            if session.user != request.user:
                 session.user = request.user
                 session.save()
            
            # SCORING: Award points via PointsService (single authority)
            if str(session.status) in ['WIN', 'LOSE'] and getattr(session, 'mode', 'hard') == 'daily':
                points = GameService.calculate_daily_score(session)
                awarded = PointsService.award_points(request.user, f"hardle_daily:{session.id}", points)
                session._awarded_points = awarded
                
            elif str(session.status) == 'WIN':
                # Legacy modes
                mode = getattr(session, 'mode', 'hard')
                points_map = {'extreme': 20, 'very_hard': 10, 'hard': 5}
                points = points_map.get(mode, 5)
                PointsService.award_points(request.user, f"hardle_{mode}", points)

        # Build end-state results (auth or anon)
        results = _get_daily_results(request, session, guess_used=payload.guess)
        
        response_data = {
            "id": session.id,
            "status": session.status,
            "guesses": session.guesses,
            "target_word": session.target_word if str(session.status) in ['WIN', 'LOSE'] else None,
            "results": results
        }
        return response_data
    except ValueError as e:
        return 400, {"message": str(e)}

@api.post("/game/reset", response=GameSessionSchema)
def reset_game(request, mode: str = 'hard'):
    session = GameService.create_session(mode=mode)
    if request.user.is_authenticated:
        session.user = request.user
        session.save()
    return session

# --- Auth Endpoints ---

@api.post("/auth/signup", response={200: UserSchema, 400: dict})
def signup(request, payload: SignupRequest):
    try:
        if User.objects.filter(username=payload.username).exists():
             return 400, {"message": "Username already taken"}
        if User.objects.filter(email=payload.email).exists():
             return 400, {"message": "Email already registered"}

        user = User.objects.create_user(
            username=payload.username,
            email=payload.email,
            password=payload.password
        )
        UserProfile.objects.create(user=user)
        login(request, user)  # Auto-login after signup
        return {"username": user.username, "email": user.email, "points": 0, "rank": "Bronze"}
    except Exception as e:
        return 400, {"message": str(e)}

@api.post("/auth/login", response={200: UserSchema, 400: dict})
def login_user(request, payload: LoginRequest):
    # Authenticate by email (find user first, then authenticate)
    try:
        user_obj = User.objects.get(email=payload.email)
        user = authenticate(username=user_obj.username, password=payload.password)
        if user:
            login(request, user)
            points = PointsService.get_user_points(user)
            return {
                "username": user.username,
                "email": user.email,
                "points": points,
                "rank": get_rank(points),
            }
        else:
            return 400, {"message": "Invalid credentials"}
    except User.DoesNotExist:
        return 400, {"message": "Invalid credentials"}

@api.get("/auth/me", response={200: UserSchema, 401: dict})
def get_me(request):
    if not request.user.is_authenticated:
        return 401, {"message": "Not authenticated"}
    
    points = PointsService.get_user_points(request.user)
        
    return {
        "username": request.user.username,
        "email": request.user.email,
        "points": points,
        "rank": get_rank(points),
    }

# --- Leaderboard ---

@api.get("/leaderboard", response=List[LeaderboardEntry])
def get_leaderboard(request, month: str = None, limit: int = 100):
    """
    Global leaderboard. Read-only aggregation.
    GET /api/leaderboard?month=2026-02&limit=50
    Defaults to current month if month is omitted.
    """
    return PointsService.get_leaderboard(month=month, limit=limit)

# Keep old endpoint for backward compat with existing frontend
@api.get("/auth/leaderboard", response=List[LeaderboardEntry])
def get_leaderboard_legacy(request):
    """Legacy endpoint — redirects to new PointsService leaderboard."""
    return PointsService.get_leaderboard(limit=10)

@api.post("/auth/logout", response={200: dict})
def logout_user(request):
    from django.contrib.auth import logout
    logout(request)
    return {"message": "Logged out successfully"}
