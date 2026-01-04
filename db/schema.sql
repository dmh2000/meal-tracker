PRAGMA foreign_keys = ON;

-- Users table
CREATE TABLE users (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    username        TEXT NOT NULL UNIQUE,
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
