CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    username TEXT UNIQUE,
    password_hash TEXT
);

CREATE TABLE matches (
    id INTEGER PRIMARY KEY,
    home_team TEXT,
    away_team TEXT,
    stadium TEXT,
    date TEXT,
    user_id INTEGER REFERENCES users,
    name TEXT
);