
export interface GameSession {
    id: string;
    status: 'IN_PROGRESS' | 'WIN' | 'LOSE';
    guesses: GuessDetail[];
    remaining_attempts?: number; // Optional helper
    target_word?: string; // Populated only on WIN/LOSE
}

export interface GuessDetail {
    word: string;
    colors: number[]; // 0=Gray, 1=Yellow, 2=Green
}

// In dev: empty string → relative URLs go through Vite proxy (same origin)
// In prod: VITE_API_URL set to full backend URL (e.g. https://api.hardle.app)
export const API_BASE = import.meta.env.VITE_API_URL ?? "";

// --- CSRF Token Management ---
let _csrfToken: string | null = null;
let _csrfFetchPromise: Promise<void> | null = null;

/** Fetch CSRF token from backend and store in memory. */
export async function ensureCsrfToken(): Promise<string> {
    if (_csrfToken) return _csrfToken;

    // Deduplicate concurrent calls
    if (!_csrfFetchPromise) {
        _csrfFetchPromise = (async () => {
            const res = await fetch(`${API_BASE}/api/auth/csrf`, {
                credentials: 'include',
            });
            if (res.ok) {
                const data = await res.json();
                _csrfToken = data.csrfToken;
            }
            _csrfFetchPromise = null;
        })();
    }
    await _csrfFetchPromise;
    return _csrfToken ?? '';
}

/** Read csrftoken from cookie as fallback. */
function getCsrfFromCookie(): string | null {
    const match = document.cookie.match(/(?:^|;\s*)csrftoken=([^;]*)/);
    return match ? decodeURIComponent(match[1]) : null;
}

// --- Internal fetch helper ---
const MUTATING_METHODS = new Set(['POST', 'PUT', 'PATCH', 'DELETE']);

async function fetchJson<T>(url: string, options?: RequestInit): Promise<T> {
    const method = (options?.method ?? 'GET').toUpperCase();

    // Build headers: always include credentials
    const headers: Record<string, string> = {
        ...(options?.headers as Record<string, string> ?? {}),
    };

    // Attach CSRF token for mutating requests
    if (MUTATING_METHODS.has(method)) {
        const token = _csrfToken ?? getCsrfFromCookie() ?? await ensureCsrfToken();
        if (token) {
            headers['X-CSRFToken'] = token;
        }
    }

    const finalOptions: RequestInit = {
        credentials: 'include',
        ...options,
        headers,
    };

    const res = await fetch(url, finalOptions);
    const contentType = res.headers.get("content-type");

    if (contentType && contentType.includes("application/json")) {
        const data = await res.json();
        if (!res.ok) {
            throw new Error(data.message || `Request failed: ${res.status}`);
        }
        return data as T;
    } else {
        if (!res.ok) {
            throw new Error(`Request failed: ${res.status} ${res.statusText}`);
        }
        throw new Error("Invalid response: Expected JSON, got " + (contentType || "unknown"));
    }
}

// --- Game API ---

export async function getGameState(sessionId?: string): Promise<GameSession> {
    let url = `${API_BASE}/api/game/state`;
    const params = new URLSearchParams();
    if (sessionId) params.append("session_id", sessionId);

    return fetchJson<GameSession>(`${url}?${params.toString()}`);
}

export async function submitGuess(sessionId: string, guess: string): Promise<GameSession> {
    return fetchJson<GameSession>(`${API_BASE}/api/game/guess?session_id=${sessionId}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ guess })
    });
}

export async function resetGame(): Promise<GameSession> {
    return fetchJson<GameSession>(`${API_BASE}/api/game/reset`, { method: 'POST' });
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
    return fetchJson<AuthResponse>(`${API_BASE}/api/auth/signup`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, email, password })
    });
}

export async function login(email: string, password: string): Promise<AuthResponse> {
    return fetchJson<AuthResponse>(`${API_BASE}/api/auth/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password })
    });
}

export async function getMe(): Promise<AuthResponse> {
    return fetchJson<AuthResponse>(`${API_BASE}/api/auth/me`);
}

export async function getLeaderboard(): Promise<LeaderboardEntry[]> {
    return fetchJson<LeaderboardEntry[]>(`${API_BASE}/api/auth/leaderboard`);
}

export async function logout(): Promise<void> {
    const token = _csrfToken ?? getCsrfFromCookie() ?? await ensureCsrfToken();
    const headers: Record<string, string> = {};
    if (token) headers['X-CSRFToken'] = token;

    const res = await fetch(`${API_BASE}/api/auth/logout`, {
        method: 'POST',
        credentials: 'include',
        headers,
    });
    if (!res.ok) throw new Error('Logout failed');
}

export async function guestLogin(): Promise<AuthResponse> {
    return fetchJson<AuthResponse>(`${API_BASE}/api/auth/guest-login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
    });
}
