from flask import Flask, render_template, request, Blueprint
import psycopg2
from config import DB_CONFIG, LEAGUES_DB


db_bp = Blueprint("db", __name__)

# ── DB standings page ─────────────────────────────────────────────────────────
def get_connection():
    return psycopg2.connect(**DB_CONFIG)

def fetch_seasons():
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT season_id, season_name FROM seasons ORDER BY season_name DESC;")
            return cur.fetchall()

def fetch_standings(season_id: int):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM get_league_table(%s);", (season_id,))
            cols = [d[0] for d in cur.description]
            rows = cur.fetchall()
    return cols, rows


# -- Route for DB standings page
@db_bp.route("/db")
def standings_db():
    seasons      = fetch_seasons()
    season_names = [season_name for _, season_name in seasons]
    season_ids   = {season_name: season_id for season_id, season_name in seasons}

    selected_league = request.args.get("league", LEAGUES_DB[0]["name"])
    selected_season = request.args.get("season", season_names[0] if season_names else None)
    season_id       = season_ids.get(selected_season)

    cols, rows = fetch_standings(season_id)
    n = len(rows)

    def row_zone(idx):
        if idx < 4:      return "zone-cl"
        if idx < 6:      return "zone-el"
        if idx >= n - 3: return "zone-rel"
        return "zone-none"

    return render_template(
        "standings_db.html",
        active_page="db",
        leagues=LEAGUES_DB,
        selected_league=selected_league,
        seasons=season_names,
        selected_season=selected_season,
        cols=cols,
        rows=rows,
        row_zone=row_zone,
        enumerate=enumerate,
    )