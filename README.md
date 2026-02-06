# Hardle v1

Hardle v1 is a **server-authoritative Wordle-style game** built as a
**foundational platform** for experimentation, analytics, and future expansion.

## Architecture
- Backend: Django 5.1 + Django Ninja (Async)
- Frontend: SvelteKit 5 (Runes)
- Database: PostgreSQL (SQLite for local dev)

## Core Principles
- Server is the single source of truth
- Client is read-only
- Dictionary validation enforced
- Experimental modes are display-only

## Status
Foundation implementation in progress.
