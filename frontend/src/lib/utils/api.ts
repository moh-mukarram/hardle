export interface GameSession {
    id: string;
    status: 'IN_PROGRESS' | 'WIN' | 'LOSE';
    guesses: GuessDetail[];
    remaining_attempts?: number; // Optional helper
}

export interface GuessDetail {
    word: string;
    colors: number[]; // 0=Gray, 1=Yellow, 2=Green
}

export const API_BASE = '/api';

export async function getGameState(sessionId?: string): Promise<GameSession> {
    const url = sessionId ? `${API_BASE}/game/state?session_id=${sessionId}` : `${API_BASE}/game/state`;
    const res = await fetch(url);
    if (!res.ok) throw new Error('Failed to fetch game state');
    return res.json();
}

export async function submitGuess(sessionId: string, guess: string): Promise<GameSession> {
    const res = await fetch(`${API_BASE}/game/guess?session_id=${sessionId}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ guess })
    });

    if (!res.ok) {
        const error = await res.json();
        throw new Error(error.message || 'Failed to submit guess');
    }
    return res.json();
}

export async function resetGame(): Promise<GameSession> {
    const res = await fetch(`${API_BASE}/game/reset`, { method: 'POST' });
    if (!res.ok) throw new Error('Failed to reset game');
    return res.json();
}

// --- Auth API ---

export interface AuthResponse {
    username: string;
    email: string;
    points: number;
}

export interface LeaderboardEntry {
    username: string;
    points: number;
}

export async function signup(username: string, email: string, password: string): Promise<AuthResponse> {
    const res = await fetch(`${API_BASE}/auth/signup`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, email, password })
    });
    if (!res.ok) {
        const error = await res.json();
        throw new Error(error.message || 'Signup failed');
    }
    return res.json();
}

export async function login(email: string, password: string): Promise<AuthResponse> {
    const res = await fetch(`${API_BASE}/auth/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password })
    });
    if (!res.ok) {
        const error = await res.json();
        throw new Error(error.message || 'Login failed');
    }
    return res.json();
}

export async function getMe(): Promise<AuthResponse> {
    const res = await fetch(`${API_BASE}/auth/me`);
    if (!res.ok) throw new Error('Not authenticated');
    return res.json();
}

export async function getLeaderboard(): Promise<LeaderboardEntry[]> {
    const res = await fetch(`${API_BASE}/auth/leaderboard`);
    if (!res.ok) throw new Error('Failed to fetch leaderboard');
    return res.json();
}

export async function logout(): Promise<void> {
    const res = await fetch(`${API_BASE}/auth/logout`, { method: 'POST' });
    if (!res.ok) throw new Error('Logout failed');
}
