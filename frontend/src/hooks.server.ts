import type { Handle } from '@sveltejs/kit';
import { env } from '$env/dynamic/private';

const BACKEND_URL = env.BACKEND_URL || 'http://127.0.0.1:8000';

export const handle: Handle = async ({ event, resolve }) => {
    // Only attempt session validation if a sessionid cookie exists
    const sessionCookie = event.cookies.get('sessionid');

    if (sessionCookie) {
        try {
            // Forward the full cookie header so Django can read the sessionid
            const res = await fetch(`${BACKEND_URL}/api/auth/me`, {
                headers: {
                    'cookie': event.request.headers.get('cookie') ?? '',
                },
            });

            if (res.ok) {
                event.locals.user = await res.json();
            } else {
                event.locals.user = null;
            }
        } catch {
            // Backend unreachable — treat as unauthenticated
            event.locals.user = null;
        }
    } else {
        event.locals.user = null;
    }

    return resolve(event);
};
