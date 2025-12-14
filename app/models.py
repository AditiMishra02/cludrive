from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from datetime import datetime

db = SQLAlchemy()
bcrypt = Bcrypt()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

    # Relationship: one user -> many files
    files = db.relationship("File", backref="user", lazy=True)


class File(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)

    filename = db.Column(db.String(255), nullable=False)
    s3_key = db.Column(db.String(500), nullable=False)

    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
