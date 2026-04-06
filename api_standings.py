from flask import Flask, render_template, request, Blueprint
import requests
from config import API_CONFIG,  LEAGUES_API, API_SEASONS


api_bp = Blueprint("api", __name__)

# ── API standings page ────────────────────────────────────────────────────────
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
            e["description"] or "",
            e["team"]["logo"] or ""
        ) for e in group]
        rows_by_group.append({"name": group_name, "rows": group_rows})

    return cols, rows_by_group



# -- Route for API standings page
@api_bp.route("/api-standings")
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