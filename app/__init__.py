from flask import Flask
from dotenv import load_dotenv
from .models import db, bcrypt
from .routes.user import user_bp
from .routes.files import files_bp

load_dotenv()

def create_app():
    app = Flask(__name__)

    # Database config
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///../cludrive.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Init DB + bcrypt
    db.init_app(app)
    bcrypt.init_app(app)

    # Register routes
    from .routes.health import health_bp
    from .routes.auth import auth_bp
    from .routes.home import home_bp

    app.register_blueprint(health_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(home_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(files_bp)

    return app

