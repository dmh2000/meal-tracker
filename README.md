# Meal Tracker

A progressive web application for tracking daily food intake and calories. Features a React/TypeScript frontend and Python/Flask backend with SQLite database.

## Features

- Track meals by type: breakfast, morning snack, lunch, afternoon snack, dinner, evening snack
- Global food database with calorie information
- Create reusable meal templates
- Daily calorie summaries
- Per-user meal logging

## Prerequisites

- Python 3.8+
- Node.js 18+
- npm

## Installation

```bash
# Install frontend dependencies
cd frontend && npm install

# Install backend dependencies
cd backend/api_server && pip install -r requirements.txt
cd backend/web_server && pip install -r requirements.txt
```

## Usage

### Development

```bash
# Terminal 1: Start API server (port 5001)
cd backend/api_server && python meals.py --port 5001

# Terminal 2: Start frontend dev server (port 5000, proxies /api to 5001)
cd frontend && npm run dev
```

### Production

```bash
./scripts/run.sh     # Build frontend and start both servers
```

## Project Structure

```
├── backend/
│   ├── api_server/      # REST API (port 5001)
│   │   ├── meals.py     # Entry point
│   │   └── routes/      # API route handlers
│   └── web_server/      # Static file server (port 5000)
├── frontend/            # React/TypeScript SPA
│   └── src/
│       ├── pages/       # Page components
│       ├── components/  # Reusable components
│       ├── services/    # API client
│       └── types/       # TypeScript definitions
├── db/
│   ├── meals.db         # SQLite database
│   └── schema.sql       # Database schema
└── scripts/             # Build and run scripts
```

## Database Tools

```bash
# Add a new food item
python db/add-food.py "Apple" 95

# List all foods as CSV
python db/list-foods.py
```

## API Endpoints

| Route | Description |
|-------|-------------|
| `/api/auth/*` | User authentication |
| `/api/foods/*` | Food items CRUD |
| `/api/meals/*` | Meal templates |
| `/api/log/*` | User daily meal logs |
