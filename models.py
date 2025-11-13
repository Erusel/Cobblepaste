from flask_sqlalchemy import SQLAlchemy
import datetime as dt

db = SQLAlchemy()


class Paste(db.Model):
    __tablename__ = "pastes"

    id = db.Column(db.Integer, primary_key=True)
    slug = db.Column(db.String(16), unique=True, nullable=False, index=True)
    title = db.Column(db.String(255), nullable=False)
    author = db.Column(db.String(255), nullable=False)
    notes = db.Column(db.Text, nullable=True)
    raw_paste = db.Column(db.Text, nullable=False)
    team_json = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=dt.datetime.utcnow)

    def __repr__(self) -> str:
        return f"<Paste {self.slug}>"
