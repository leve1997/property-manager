import os
from flask import Flask
from dotenv import load_dotenv

load_dotenv()

def create_app():
    app = Flask(__name__, instance_relative_config=True, template_folder='../templates')
    app.secret_key = os.environ['SECRET_KEY']

    from api.auth import auth_bp
    app.register_blueprint(auth_bp)

    from api.activities import activities_bp
    app.register_blueprint(activities_bp)

    return app

