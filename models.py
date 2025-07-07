from datetime import datetime, timezone
from  werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'user'
    user_id = db.Column(db.Integer, primary_key=True)
    handle = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Note(db.Model):
    __tablename__ = 'note'
    note_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False)
    contest_id = db.Column(db.Integer, nullable=False)
    problem_index = db.Column(db.String, nullable=False)
    problem_name = db.Column(db.String, nullable=False)
    content = db.Column(db.String(5000))
    timestamp = db.Column(db.DateTime, default=datetime.now(timezone.utc))
