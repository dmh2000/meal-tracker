PRAGMA foreign_keys = ON;

-- users
CREATE TABLE users (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    username        TEXT NOT NULL UNIQUE,
    password_hash   BLOB NOT NULL,
    password_salt   BLOB NOT NULL,
);

-- user meal log
CREATE TABLE user_meal_log (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id         INTEGER NOT NULL,
    meal_id         INTEGER NOT NULL,
    logged_at       TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now')),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (meal_id) REFERENCES meals(id) ON DELETE CASCADE
);

-- foods
CREATE TABLE foods (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    name            TEXT NOT NULL,
    calories        INTEGER NOT NULL, -- calories per unit (e.g., per serving)
);

-- meals
CREATE TABLE meals (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    name            TEXT,
    description     TEXT,
);

-- Join table: many-to-many between meals and foods
CREATE TABLE meal_items (
    meal_id         INTEGER NOT NULL,
    food_id         INTEGER NOT NULL,
    PRIMARY KEY (meal_id, food_id),
    FOREIGN KEY (meal_id) REFERENCES meals(id) ON DELETE CASCADE,
    FOREIGN KEY (food_id) REFERENCES foods(id) ON DELETE RESTRICT
);

CREATE INDEX idx_meal_items_food_id ON meal_items(food_id);

SELECT
    m.id,
    m.name,
    SUM(f.calories * mi.quantity) AS total_calories
FROM meals AS m
JOIN meal_items AS mi ON mi.meal_id = m.id
JOIN foods AS f ON f.id = mi.food_id
WHERE m.id = ?
GROUP BY m.id, m.name;


SELECT
    m.user_id,
    date(m.eaten_at) AS day,
    SUM(f.calories * mi.quantity) AS total_calories
FROM meals AS m
JOIN meal_items AS mi ON mi.meal_id = m.id
JOIN foods AS f ON f.id = mi.food_id
WHERE m.user_id = ?
GROUP BY m.user_id, date(m.eaten_at);
