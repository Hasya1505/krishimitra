"""
init_db.py - creates the KrishiMitra SQLite schema if it doesn't already exist.
Run standalone (python database/init_db.py) or imported and called from app.py.
"""
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent / "krishimitra.db"

SCHEMA = """
CREATE TABLE IF NOT EXISTS users (
  id            INTEGER PRIMARY KEY AUTOINCREMENT,
  name          TEXT NOT NULL,
  phone         TEXT UNIQUE,
  email         TEXT UNIQUE,
  password_hash TEXT NOT NULL,
  state         TEXT,
  district      TEXT,
  created_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS crop_queries (
  id            INTEGER PRIMARY KEY AUTOINCREMENT,
  user_id       INTEGER REFERENCES users(id),
  state         TEXT,
  district      TEXT,
  season        TEXT,
  n             REAL, p REAL, k REAL, ph REAL,
  temperature   REAL,
  humidity      REAL,
  rainfall      REAL,
  top_crop      TEXT,
  results_json  TEXT,
  queried_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS soil_queries (
  id                INTEGER PRIMARY KEY AUTOINCREMENT,
  user_id           INTEGER REFERENCES users(id),
  crop              TEXT,
  soil_type         TEXT,
  n                 REAL, p REAL, k REAL, ph REAL,
  organic_carbon    REAL,
  ec                REAL,
  health_score      REAL,
  suggestions_json  TEXT,
  queried_at        TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"""


def init_db():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.executescript(SCHEMA)
    conn.commit()
    conn.close()
    print(f"Database ready at {DB_PATH}")


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


if __name__ == "__main__":
    init_db()
