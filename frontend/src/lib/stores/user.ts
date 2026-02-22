import { writable } from 'svelte/store';
import { browser } from '$app/environment';

export type UserRank = 'guest' | 'user' | 'sudo' | 'admin' | 'root';

export interface UserState {
    name: string;
    rank: UserRank;
    points: number;
}

const defaultState: UserState = {
    name: 'RYU',
    rank: 'user',
    points: 450
};

// Start with default, but hydrate from localStorage if available
const initialValue: UserState = browser && localStorage.getItem('hardle_user_state')
    ? JSON.parse(localStorage.getItem('hardle_user_state') as string)
    : defaultState;

export const userStore = writable<UserState>(initialValue);

// Subscribe to changes and selectively mirror to localStorage
if (browser) {
    userStore.subscribe((value) => {
        localStorage.setItem('hardle_user_state', JSON.stringify(value));
    });
}
