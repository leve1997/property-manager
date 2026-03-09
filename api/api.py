import os
import logging
from flask import Flask, send_from_directory
from dotenv import load_dotenv

load_dotenv()

def create_app():
    app = Flask(__name__, instance_relative_config=True, template_folder='../templates', static_folder='../static')
    app.secret_key = os.environ['SECRET_KEY']

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s %(levelname)s %(name)s: %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
    )

    from api.auth import auth_bp
    app.register_blueprint(auth_bp)

    from api.activities import activities_bp
    app.register_blueprint(activities_bp)

    @app.route('/service-worker.js')
    def service_worker():
        return send_from_directory(app.static_folder, 'service-worker.js',
                                   mimetype='application/javascript')

    return app

