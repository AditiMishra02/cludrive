from app import create_app
from app.models import db

app = create_app()

with app.app_context():
    print("Dropping existing tables...")
    db.drop_all()

    print("Creating new tables...")
    db.create_all()

    print("Database tables created successfully!")
