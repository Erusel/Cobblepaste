import os
import json
import secrets
import string
import datetime as dt

from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    abort,
    flash,
)
from models import db, Paste
from parser import parse_showdown_team

def create_app():
    app = Flask(__name__)

    app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "change-me-in-prod")

    if "DATABASE_URL" in os.environ:
        db_url = os.environ["DATABASE_URL"]

        # Fix Heroku-style URLs
        if db_url.startswith("postgres://"):
            db_url = db_url.replace("postgres://", "postgresql://", 1)
    else:
        # Local SQLite: writes the DB file inside your project folder
        db_path = os.path.join(os.path.dirname(__file__), "cobblepaste.db")
        db_url = f"sqlite:///{db_path}"

    app.config["SQLALCHEMY_DATABASE_URI"] = db_url
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)

    with app.app_context():
        db.create_all()

    # -------- Helpers -------- #

    def generate_slug(length: int = 8) -> str:
        alphabet = string.ascii_uppercase + string.digits
        while True:
            slug = "".join(secrets.choice(alphabet) for _ in range(length))
            if not Paste.query.filter_by(slug=slug).first():
                return slug

    # -------- Routes -------- #

    @app.get("/")
    def index():
        return render_template("index.html")

    @app.post("/")
    def create_paste():
        title = request.form.get("title", "").strip() or "Untitled team"
        author = request.form.get("author", "").strip() or "Anonymous"
        notes = request.form.get("notes", "").strip()
        competitive_mode = request.form.get("competitive_mode") == "on"
        raw_paste = request.form.get("paste", "").strip()

        if not raw_paste:
            flash("Please paste a Pokémon Showdown team.", "error")
            return redirect(url_for("index"))

        try:
            team = parse_showdown_team(raw_paste)
            if not team:
                raise ValueError("No Pokémon found in the paste.")
        except Exception as e:
            flash(f"Could not parse your team: {e}", "error")
            return redirect(url_for("index"))

        slug = generate_slug()
        paste = Paste(
            slug=slug,
            title=title,
            author=author,
            notes=notes,
            raw_paste=raw_paste,
            team_json=json.dumps(team),
            competitive_mode=competitive_mode,
            created_at=dt.datetime.utcnow(),
        )
        db.session.add(paste)
        db.session.commit()

        # Redirect to the pretty view
        return redirect(url_for("view_paste", slug=slug))

    @app.get("/<slug>")
    def view_paste(slug):
        paste = Paste.query.filter_by(slug=slug).first()
        if not paste:
            abort(404)

        team = json.loads(paste.team_json)
        return render_template(
            "paste.html",
            paste=paste,
            team=team,
        )

    @app.errorhandler(404)
    def not_found(e):
        return render_template("404.html"), 404

    return app


app = create_app()

if __name__ == "__main__":
    # For local dev only; in Dokploy you'll run via gunicorn
    app.run(host="0.0.0.0", port=8000, debug=True)
