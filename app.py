from flask import Flask, render_template
from db_standings import db_bp
from api_standings import api_bp

app = Flask(__name__)
app.register_blueprint(db_bp)
app.register_blueprint(api_bp)

# ── Landing page ──────────────────────────────────────────────────────────────
@app.route("/")
def landing():
    return render_template("landing.html", active_page="home")

if __name__ == "__main__":
    app.run(debug=True, port=5050)