# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Meal Tracker is a progressive web application for tracking daily food intake and calories. It features a React/TypeScript frontend and a Python/Flask backend with SQLite database.

## Commands

### Development
```bash
# Frontend dev server (port 5000, proxies /api to 5001)
cd frontend && npm run dev

# API server
cd backend/api_server && python app.py --port 5001

# Build frontend for production
cd frontend && npm run build
```

### Production
```bash
./scripts/build.sh   # Build frontend
./scripts/run.sh     # Build and start both servers
```

### Install Dependencies
```bash
cd frontend && npm install
cd backend/api_server && pip install -r requirements.txt
cd backend/web_server && pip install -r requirements.txt
```

## Architecture

### Two-Server Backend Design
- **Web Server** (`backend/web_server/server.py`, port 5000): Serves static frontend assets and proxies `/api/*` requests to the API server
- **API Server** (`backend/api_server/app.py`, port 5001): Handles all business logic and database operations

### Frontend Structure
- React 18 with TypeScript (strict mode)
- Vite build tool with Tailwind CSS
- React Router for SPA routing
- Auth state managed via `AuthContext`
- API calls in `frontend/src/services/api.ts`

### Database
- SQLite at `db/meals.db`
- Schema defined in `db/schema.sql`
- Database initialized automatically on first API server start
- Key tables: `users`, `sessions`, `foods`, `meals`, `meal_items`, `user_meal_log`, `user_meal_log_items`

### API Routes
Routes defined in `backend/api_server/routes/`:
- `auth_routes.py`: `/api/auth/*` - registration, login, logout, session validation
- `food_routes.py`: `/api/foods/*` - global food items CRUD
- `meal_routes.py`: `/api/meals/*` - global meal templates
- `log_routes.py`: `/api/log/*` - user's daily meal logs

### Data Model Concepts
- **Foods**: Global, shared across all users
- **Meal Templates**: Named meals with descriptions, shared globally
- **User Meal Log**: Per-user daily tracking by meal type (breakfast, morning_snack, lunch, afternoon_snack, dinner, evening_snack)
- One log entry per meal type per day per user

## Key Patterns

- Frontend uses relative `/api` paths; Vite dev server proxies to port 5001
- Session tokens stored in HTTP-only cookies
- All database queries use parameterized statements via `database.py` helpers
- TypeScript types defined in `frontend/src/types/index.ts`
