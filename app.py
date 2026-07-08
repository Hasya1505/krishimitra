"""
app.py - KrishiMitra Flask application entry point
"""
from flask import Flask
from flask_login import LoginManager

from config import Config
from database.init_db import init_db
from routes.auth import auth_bp, load_user_by_id
from routes.crop import crop_bp
from routes.soil import soil_bp
from routes.weather import weather_bp
from routes.main import main_bp


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    init_db()

    login_manager = LoginManager()
    login_manager.login_view = "auth.login"
    login_manager.login_message = "Please log in to access KrishiMitra."
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return load_user_by_id(user_id)

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(crop_bp)
    app.register_blueprint(soil_bp)
    app.register_blueprint(weather_bp)

    return app


app = create_app()

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
