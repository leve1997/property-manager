from flask import Flask, render_template
from flask_cors import CORS
import secrets
from api.api import api_bp

app = Flask(__name__)

# Session configuration
app.secret_key = secrets.token_hex(32)
app.config["SESSION_COOKIE_SECURE"] = False
app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
app.config["SESSION_PERMANENT"] = True

# CORS configuration
CORS(
    app,
    supports_credentials=True,
    origins=["http://localhost:8000", "http://127.0.0.1:8000"],
    allow_headers=["Content-Type"],
    methods=["GET", "POST", "OPTIONS"],
)

# Register API blueprint
app.register_blueprint(api_bp)


@app.route("/")
def hello_world():
    return render_template("index.html")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)