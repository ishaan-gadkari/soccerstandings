from flask import Flask, render_template, request
import psycopg2
import requests
from config import DB_CONFIG, API_CONFIG, LEAGUES_DB, LEAGUES_API, API_SEASONS

app = Flask(__name__)

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

def fetch_api_standings(league_id, season):
    url = f"{API_CONFIG['API_URL']}/standings"
    headers = {"x-apisports-key": API_CONFIG["API_KEY"]}
    params  = {"league": league_id, "season": season}
    response = requests.get(url, headers=headers, params=params, timeout=10)
    response.raise_for_status()
    data = response.json()
    
    groups = data["response"][0]["league"]["standings"]
    cols = ["POS", "TEAM", "PLD", "WON", "DRN", "LST", "FOR", "AG", "GD", "PTS"]

    rows_by_group = []
    for group in groups:
        group_name = group[0]["group"]
        group_rows = [(
            e["rank"], e["team"]["name"],
            e["all"]["played"], e["all"]["win"], e["all"]["draw"], e["all"]["lose"],
            e["all"]["goals"]["for"], e["all"]["goals"]["against"],
            e["goalsDiff"], e["points"],
            e["description"] or ""
        ) for e in group]
        rows_by_group.append({"name": group_name, "rows": group_rows})

    return cols, rows_by_group

# ── Landing page ──────────────────────────────────────────────────────────────
@app.route("/")
def landing():
    return render_template("landing.html", active_page="home")

# ── DB standings page ─────────────────────────────────────────────────────────
@app.route("/db")
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

# ── API standings page ────────────────────────────────────────────────────────
@app.route("/api-standings")
def standings_api():
    selected_league_name = request.args.get("league", LEAGUES_API[0]["name"])
    selected_season      = request.args.get("season", str(API_SEASONS[0]))

    league_id = next((l["id"] for l in LEAGUES_API if l["name"] == selected_league_name), LEAGUES_API[0]["id"])

    cols, groups = fetch_api_standings(league_id, selected_season)

    def row_zone(row):
        desc = row[10] or ""
        if "Champions League" in desc: return "zone-cl"
        if "Europa League"    in desc: return "zone-el"
        if "Bundesliga (Relegation)" in desc: return "zone-none"
        if "Relegation"       in desc: return "zone-rel"


        return "zone-none"

    return render_template(
        "standings_api.html",
        active_page="api",
        leagues=LEAGUES_API,
        selected_league=selected_league_name,
        seasons=API_SEASONS,
        selected_season=selected_season,
        cols=cols,
        groups=groups,
        row_zone=row_zone,
        enumerate=enumerate,
    )


if __name__ == "__main__":
    app.run(debug=True, port=5050)