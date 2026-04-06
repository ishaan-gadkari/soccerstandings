from dotenv import load_dotenv
import os

load_dotenv("config.env")

print(os.getenv("DB_NAME"))
print(os.getenv("API_KEY"))

DB_CONFIG = {
    "host":     "localhost",
    "port":     5432,
    "dbname":   os.getenv("DB_NAME"),
    "user":     os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
}

API_CONFIG = {
    "API_URL": "https://v3.football.api-sports.io",
    "API_KEY": os.getenv("API_KEY"),
}

# ── Leagues (replace with API call later) ─────────────────────────────────────
LEAGUES_DB = [
    { "id": 1, "name": "English Premier League" },
]

LEAGUES_API = [
    { "id": 39, "name": "English Premier League" },
    { "id": 61, "name": "French Ligue 1" },
    { "id": 78, "name": "German Bundesliga" },
    { "id": 135, "name": "Italian Serie A" },
    { "id": 140, "name": "Spanish La Liga" },
    { "id": 2, "name": "UEFA Champions League" },
    { "id": 3, "name": "UEFA Europa League" }
]


# Seasons available in the dropdown
API_SEASONS = [2024, 2023, 2022]



