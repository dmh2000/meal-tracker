# Meal Tracker - Progressive Web Application Specification

## Overview

Build a progressive single-page web application for tracking daily food intake, calories, and meals. The application supports multiple users with persistent login sessions. Food items and named meals are shared globally across all users.

---

## Technology Stack

### Frontend
- **Build Tool**: Vite
- **Language**: TypeScript (strict mode)
- **Framework**: React 18+
- **Styling**: Tailwind CSS
- **State Management**: React Context (for auth state)
- **HTTP Client**: Fetch API
- **PWA**: Service worker for offline capability and installability

### Backend - Web Server
- **Language**: Python 3.10+
- **Framework**: Flask
- **Purpose**: Serve the static frontend assets
- **Configuration**: Command-line argument `--port` for listening port (default: 5000)

### Backend - Database API Server
- **Language**: Python 3.10+
- **Framework**: Flask
- **Database**: SQLite3
- **Configuration**: Command-line argument `--port` for listening port (default: 5001)
- **Authentication**: JWT tokens stored in HTTP-only cookies

---

## Database Schema

```sql
PRAGMA foreign_keys = ON;

-- Users table
CREATE TABLE users (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    username        TEXT NOT NULL UNIQUE,
    password_hash   BLOB NOT NULL,
    password_salt   BLOB NOT NULL,
    created_at      TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now'))
);

-- Session tokens for "remember me" functionality
CREATE TABLE sessions (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id         INTEGER NOT NULL,
    token           TEXT NOT NULL UNIQUE,
    expires_at      TEXT NOT NULL,
    created_at      TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now')),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE INDEX idx_sessions_token ON sessions(token);
CREATE INDEX idx_sessions_user_id ON sessions(user_id);

-- Foods table (global, shared across all users)
CREATE TABLE foods (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    name            TEXT NOT NULL UNIQUE,
    calories        INTEGER NOT NULL,
    created_at      TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now'))
);

CREATE INDEX idx_foods_name ON foods(name);

-- Meals table (global templates, shared across all users)
-- Only meals with a name are stored here for reuse
CREATE TABLE meals (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    name            TEXT NOT NULL UNIQUE,
    description     TEXT,
    created_at      TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now'))
);

CREATE INDEX idx_meals_name ON meals(name);

-- Meal items: foods that make up a meal template
CREATE TABLE meal_items (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    meal_id         INTEGER NOT NULL,
    food_id         INTEGER NOT NULL,
    quantity        REAL NOT NULL DEFAULT 1.0,
    FOREIGN KEY (meal_id) REFERENCES meals(id) ON DELETE CASCADE,
    FOREIGN KEY (food_id) REFERENCES foods(id) ON DELETE RESTRICT
);

CREATE INDEX idx_meal_items_meal_id ON meal_items(meal_id);
CREATE INDEX idx_meal_items_food_id ON meal_items(food_id);

-- User daily meal log
-- Tracks what each user ate for each meal type on each day
-- meal_type: 'breakfast', 'morning_snack', 'lunch', 'afternoon_snack', 'dinner', 'evening_snack'
CREATE TABLE user_meal_log (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id         INTEGER NOT NULL,
    meal_date       TEXT NOT NULL,
    meal_type       TEXT NOT NULL CHECK (meal_type IN ('breakfast', 'morning_snack', 'lunch', 'afternoon_snack', 'dinner', 'evening_snack')),
    meal_id         INTEGER,
    created_at      TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now')),
    updated_at      TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now')),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (meal_id) REFERENCES meals(id) ON DELETE SET NULL,
    UNIQUE (user_id, meal_date, meal_type)
);

CREATE INDEX idx_user_meal_log_user_date ON user_meal_log(user_id, meal_date);

-- User meal log items: individual food items for a user's logged meal
-- Allows users to log food items directly without creating a named meal
CREATE TABLE user_meal_log_items (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    log_id          INTEGER NOT NULL,
    food_id         INTEGER NOT NULL,
    quantity        REAL NOT NULL DEFAULT 1.0,
    FOREIGN KEY (log_id) REFERENCES user_meal_log(id) ON DELETE CASCADE,
    FOREIGN KEY (food_id) REFERENCES foods(id) ON DELETE RESTRICT
);

CREATE INDEX idx_user_meal_log_items_log_id ON user_meal_log_items(log_id);
```

### Schema Design Notes

1. **Global Foods**: All food items are shared across users. Any user can add new foods.
2. **Global Meals**: Named meals (templates) are shared. Only meals with a name are stored in the `meals` table.
3. **User Meal Log**: Links users to their daily food intake by meal type and date.
4. **Flexible Logging**: Users can either:
   - Select a named meal template (populates from `meal_items`)
   - Add individual food items directly (stored in `user_meal_log_items`)
   - Or both
5. **Quantity Support**: Both `meal_items` and `user_meal_log_items` have quantity fields for portion control.
6. **One Entry Per Meal Type Per Day**: UNIQUE constraint ensures each user has at most one log entry per meal type per day.

---

## API Endpoints

### Authentication

#### POST /api/auth/register
Register a new user.
```json
Request:  { "username": "string", "password": "string" }
Response: { "id": number, "username": "string" }
Errors:   400 (username exists), 400 (validation failed)
```

#### POST /api/auth/login
Login and receive auth token.
```json
Request:  { "username": "string", "password": "string", "remember_me": boolean }
Response: { "id": number, "username": "string" }
```
- Sets HTTP-only cookie with session token
- If `remember_me` is true, session expires in 30 days; otherwise 24 hours

#### POST /api/auth/logout
Logout and invalidate session.
```json
Response: { "success": true }
```

#### GET /api/auth/me
Get current authenticated user (validates session).
```json
Response: { "id": number, "username": "string" } | 401 Unauthorized
```

---

### Foods (Global)

#### GET /api/foods
Get all food items.
```json
Response: [{ "id": number, "name": "string", "calories": number }]
```

#### GET /api/foods/search?q=query
Search foods by name.
```json
Response: [{ "id": number, "name": "string", "calories": number }]
```

#### POST /api/foods
Create a new food item.
```json
Request:  { "name": "string", "calories": number }
Response: { "id": number, "name": "string", "calories": number }
Errors:   400 (name exists), 400 (validation failed)
```

---

### Meals (Global Templates)

#### GET /api/meals
Get all named meal templates (only those with descriptions for template selection).
```json
Response: [{
  "id": number,
  "name": "string",
  "description": "string",
  "items": [{ "food_id": number, "food_name": "string", "calories": number, "quantity": number }],
  "total_calories": number
}]
```

#### GET /api/meals/:id
Get a specific meal template.
```json
Response: {
  "id": number,
  "name": "string",
  "description": "string|null",
  "items": [...],
  "total_calories": number
}
```

#### POST /api/meals
Create a new named meal template.
```json
Request: {
  "name": "string",
  "description": "string|null",
  "items": [{ "food_id": number, "quantity": number }]
}
Response: { "id": number, "name": "string", ... }
Errors:   400 (name exists)
```

---

### User Meal Log (Per User)

#### GET /api/log?date=YYYY-MM-DD
Get user's meal log for a specific date (defaults to today).
```json
Response: {
  "date": "YYYY-MM-DD",
  "total_calories": number,
  "meals": {
    "breakfast": { "log_id": number|null, "meal_name": "string|null", "items": [...], "calories": number },
    "morning_snack": { ... },
    "lunch": { ... },
    "afternoon_snack": { ... },
    "dinner": { ... },
    "evening_snack": { ... }
  }
}
```

#### GET /api/log/:log_id
Get a specific meal log entry with all items.
```json
Response: {
  "id": number,
  "meal_date": "YYYY-MM-DD",
  "meal_type": "string",
  "meal_id": number|null,
  "meal_name": "string|null",
  "items": [{ "id": number, "food_id": number, "food_name": "string", "calories": number, "quantity": number }],
  "total_calories": number
}
```

#### POST /api/log
Create or update a meal log entry for the current date.
```json
Request: {
  "meal_type": "string",
  "meal_date": "YYYY-MM-DD",
  "meal_id": number|null,
  "meal_name": "string|null",
  "items": [{ "food_id": number, "quantity": number }]
}
Response: { "id": number, ... }
Errors:   400 (date is not today), 400 (validation failed)
```
- If `meal_name` is provided and meal doesn't exist, creates a new global meal template
- If `meal_id` is provided, copies items from that template (user can modify)
- `items` array contains the actual foods logged (can differ from template)
- Uses UPSERT: creates if doesn't exist, updates if exists for that user/date/type

#### DELETE /api/log/:log_id
Delete a meal log entry (only allowed for current date).
```json
Response: { "success": true }
Errors:   403 (not today's meal), 404 (not found)
```

---

## Frontend Architecture

### Routes/Pages

1. **`/login`** - Login Page
   - Username and password input fields
   - "Remember me" checkbox
   - Login button
   - Link to registration page
   - Redirect to dashboard if already authenticated

2. **`/register`** - Registration Page
   - Username input
   - Password input with confirmation
   - Register button
   - Link to login page

3. **`/`** - Dashboard (Protected)
   - Display current date prominently
   - Total daily calories in large display
   - Six meal cards/buttons arranged in a grid:
     - Meal type name (Breakfast, Morning Snack, etc.)
     - Calorie count for that meal
     - Visual indicator (checkmark/color) if meal has been logged
     - Clicking opens the meal entry page
   - Logout button in header

4. **`/meal/:type`** - Meal Entry Page (Protected)
   - Header showing meal type (e.g., "Breakfast")
   - Current total calories for this meal
   - **Meal Name Input** (optional)
     - If filled, meal template can be saved for reuse
   - **Load from Template** dropdown/modal
     - Shows meals that have a description
     - Selecting populates food items list
   - **Food Items List**
     - Each row: food name, calories, quantity input, remove button
     - Running total updates as items change
   - **Add Food Section**
     - Searchable dropdown of existing foods
     - "Add" button to add selected food
     - Expandable "Create New Food" form (name, calories)
   - **Save Button** - saves the meal log
   - **Back Link** - returns to dashboard
   - Only editable for current date

5. **`/foods`** - Foods Management (Optional, Protected)
   - List of all available foods
   - Search/filter
   - Add new food form

### Component Structure

```
src/
├── components/
│   ├── ui/
│   │   ├── Button.tsx
│   │   ├── Input.tsx
│   │   ├── Card.tsx
│   │   ├── Modal.tsx
│   │   ├── Select.tsx
│   │   └── Spinner.tsx
│   ├── auth/
│   │   ├── LoginForm.tsx
│   │   ├── RegisterForm.tsx
│   │   └── ProtectedRoute.tsx
│   ├── meals/
│   │   ├── MealCard.tsx
│   │   ├── MealItemList.tsx
│   │   ├── MealItemRow.tsx
│   │   ├── FoodSelector.tsx
│   │   ├── NewFoodForm.tsx
│   │   └── TemplateSelector.tsx
│   └── layout/
│       ├── Header.tsx
│       └── Layout.tsx
├── pages/
│   ├── LoginPage.tsx
│   ├── RegisterPage.tsx
│   ├── DashboardPage.tsx
│   └── MealPage.tsx
├── hooks/
│   ├── useAuth.ts
│   ├── useMealLog.ts
│   └── useFoods.ts
├── context/
│   └── AuthContext.tsx
├── services/
│   └── api.ts
├── types/
│   └── index.ts
├── App.tsx
└── main.tsx
```

### TypeScript Types

```typescript
type MealType = 'breakfast' | 'morning_snack' | 'lunch' | 'afternoon_snack' | 'dinner' | 'evening_snack';

interface User {
  id: number;
  username: string;
}

interface Food {
  id: number;
  name: string;
  calories: number;
}

interface MealItem {
  id?: number;
  food_id: number;
  food_name: string;
  calories: number;
  quantity: number;
}

interface MealTemplate {
  id: number;
  name: string;
  description: string | null;
  items: MealItem[];
  total_calories: number;
}

interface MealLogEntry {
  log_id: number | null;
  meal_name: string | null;
  items: MealItem[];
  calories: number;
}

interface DailyLog {
  date: string;
  total_calories: number;
  meals: Record<MealType, MealLogEntry>;
}
```

---

## Business Rules

1. **Meal Editing Restriction**: Users can only create/modify meal logs for the current local date. Previous days are read-only.

2. **One Meal Per Type Per Day**: Each meal type has exactly one log entry per day per user.

3. **Global Food Items**: All food items are shared. Any user can create new foods, visible to all.

4. **Global Meal Templates**: Named meals with descriptions are shared templates. Any user can create and use them.

5. **Meal Naming**:
   - If a user names a meal, it becomes a reusable template
   - Only meals with a description appear in the template selection list
   - Unnamed meals are just logged without creating a template

6. **Template Population**: Selecting a template populates the food items, but the user can modify them before saving.

7. **Session Persistence**: "Remember me" creates a 30-day session; otherwise session expires in 24 hours.

8. **Quantity Handling**: Food quantities are decimal (0.5 for half serving, 2.0 for double, etc.).

9. **Calorie Calculation**: `total = sum(food.calories * item.quantity)`

---

## Security Requirements

1. **Password Storage**: Use bcrypt with cost factor 12+ or Argon2id
2. **Session Tokens**: Cryptographically random tokens (32+ bytes), stored hashed in database
3. **HTTP-Only Cookies**: Session tokens in HTTP-only, Secure, SameSite=Strict cookies
4. **Input Validation**: Validate all inputs on server side
5. **SQL Injection Prevention**: Use parameterized queries exclusively
6. **CORS**: Same-origin only, or explicitly configured allowed origins
7. **Rate Limiting**: Limit login attempts (5 per minute per IP)

---

## PWA Requirements

1. **manifest.json**: App name, icons (192x192, 512x512), theme color, background color, display: standalone
2. **Service Worker**: Cache static assets, enable offline viewing of previously loaded data
3. **Responsive Design**: Mobile-first, usable on screens from 320px to desktop
4. **Installable**: Meets PWA install criteria for Add to Home Screen

---

## Project Structure

```
meals/
├── frontend/
│   ├── public/
│   │   ├── manifest.json
│   │   ├── sw.js
│   │   └── icons/
│   ├── src/
│   │   └── (see Component Structure above)
│   ├── index.html
│   ├── vite.config.ts
│   ├── tailwind.config.js
│   ├── postcss.config.js
│   ├── tsconfig.json
│   └── package.json
├── backend/
│   ├── web_server/
│   │   ├── server.py
│   │   └── requirements.txt
│   └── api_server/
│       ├── app.py
│       ├── auth.py
│       ├── database.py
│       ├── routes/
│       │   ├── auth_routes.py
│       │   ├── food_routes.py
│       │   ├── meal_routes.py
│       │   └── log_routes.py
│       ├── requirements.txt
│       └── schema.sql
├── db/
│   └── meals.db
└── prompts/
    ├── draft.md
    └── app.md
```

---

## Running the Application

### Development
```bash
# Terminal 1: API server
cd backend/api_server
pip install -r requirements.txt
python app.py --port 5001

# Terminal 2: Web server
cd backend/web_server
pip install -r requirements.txt
python server.py --port 5000

# Terminal 3: Frontend dev server (with hot reload, proxies to API)
cd frontend
npm install
npm run dev
```

### Production
```bash
# Build frontend
cd frontend && npm run build

# Copy to web server
cp -r dist/* ../backend/web_server/static/

# Run servers
python backend/api_server/app.py --port 5001 &
python backend/web_server/server.py --port 5000
```

---

## Implementation Phases

### Phase 1: Database & Authentication
- Set up SQLite database with complete schema
- Implement user registration and login
- Session management with "remember me"
- Basic Flask API structure

### Phase 2: Food & Meal APIs
- Foods CRUD endpoints
- Meal template CRUD endpoints
- User meal log endpoints

### Phase 3: Frontend Foundation
- Vite + React + TypeScript + Tailwind setup
- React Router configuration
- Auth context and protected routes
- Login and registration pages

### Phase 4: Core Features
- Dashboard with meal cards
- Meal entry page with food selection
- Template loading functionality
- New food creation

### Phase 5: Polish & PWA
- PWA manifest and service worker
- Responsive design refinements
- Loading states and error handling
- Form validation feedback
- Modern, simple, and attractive user interface:
  - Clean visual hierarchy with ample whitespace
  - Consistent color scheme with accent colors for actions
  - Smooth transitions and micro-animations
  - Clear typography with readable font sizes
  - Intuitive iconography for meal types and actions
  - Card-based layout with subtle shadows and rounded corners
  - Mobile-friendly touch targets (min 44px)
  - Visual feedback on interactions (hover, focus, active states)
