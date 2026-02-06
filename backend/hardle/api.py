from ninja import NinjaAPI, Router
from django.shortcuts import get_object_or_404
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.db import IntegrityError
from .models import GameSession, UserProfile
from .schemas import (
    GameSessionSchema, GuessRequest, 
    SignupRequest, LoginRequest, UserSchema, LeaderboardEntry
)
from .services import GameService
from typing import List

api = NinjaAPI(title="Hardle v1.0 API")

# --- Game Router ---
@api.get("/game/state", response=GameSessionSchema)
def get_game_state(request, session_id: str = None):
    # Session loading logic similar to previous version
    session = None
    if session_id:
        session = GameService.get_session(session_id)
    
    if not session:
        session = GameService.create_session()
        # If user is authenticated, link session
        if request.user.is_authenticated:
            session.user = request.user
            session.save()
            
    return session

@api.post("/game/guess", response={200: GameSessionSchema, 400: dict})
def submit_guess(request, payload: GuessRequest, session_id: str):
    try:
        session = GameService.process_guess(session_id, payload.guess)
        if request.user.is_authenticated and session.user != request.user:
            # Re-link just in case
             session.user = request.user
             session.save()
        return session
    except ValueError as e:
        return 400, {"message": str(e)}

@api.post("/game/reset", response=GameSessionSchema)
def reset_game(request):
    session = GameService.create_session()
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
        return {"username": user.username, "email": user.email, "points": 0}
    except Exception as e:
        return 400, {"message": str(e)}

@api.post("/auth/login", response={200: UserSchema, 400: dict})
def login_user(request, payload: LoginRequest):
    # Authenticate by email (requires finding user first or custom backend, 
    # but for simplicity we'll try to find user by email first)
    try:
        user_obj = User.objects.get(email=payload.email)
        user = authenticate(username=user_obj.username, password=payload.password)
        if user:
            login(request, user)
            points = 0
            if hasattr(user, 'profile'):
                points = user.profile.points
            return {"username": user.username, "email": user.email, "points": points}
        else:
            return 400, {"message": "Invalid credentials"}
    except User.DoesNotExist:
        return 400, {"message": "Invalid credentials"}

@api.get("/auth/me", response={200: UserSchema, 401: dict})
def get_me(request):
    if not request.user.is_authenticated:
        return 401, {"message": "Not authenticated"}
    
    points = 0
    if hasattr(request.user, 'profile'):
        points = request.user.profile.points
        
    return {
        "username": request.user.username,
        "email": request.user.email,
        "points": points
    }

@api.get("/auth/leaderboard", response=List[LeaderboardEntry])
def get_leaderboard(request):
    # Return top 10 sorted by points desc
    profiles = UserProfile.objects.select_related('user').order_by('-points')[:10]
    return [
        {"username": p.user.username, "points": p.points}
        for p in profiles
    ]

@api.post("/auth/logout", response={200: dict})
def logout_user(request):
    from django.contrib.auth import logout
    logout(request)
    return {"message": "Logged out successfully"}

