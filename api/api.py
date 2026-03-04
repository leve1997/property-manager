from flask import Flask
from flask_cors import CORS

def create_app():
    app = Flask(__name__, instance_relative_config=True)

    CORS(
    app,
    supports_credentials=True,
    resources={r"/api/*": {"origins": ["http://localhost:8000", "http://127.0.0.1:8000"]}}, # Update for production
    allow_headers=["Content-Type", "Authorization"],
    methods=["GET", "POST", "OPTIONS"],
    expose_headers=["Content-Type"],
    max_age=3600
)

    from api.auth import auth_bp
    app.register_blueprint(auth_bp)

    from api.activities import activities_bp
    app.register_blueprint(activities_bp)

    return app

