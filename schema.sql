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
    name TEXT,
    atmosphere_rating INTEGER,
    notes TEXT
);

CREATE TABLE likes (
    match_id INTEGER REFERENCES matches,
    user_id INTEGER REFERENCES users,
    created_at TEXT,
    PRIMARY KEY (match_id, user_id)  
);