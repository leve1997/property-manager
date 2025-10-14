from flask import Flask, render_template
from flask_cors import CORS
from api.api import api_bp

app = Flask(__name__)

# CORS configuration
CORS(
    app,
    supports_credentials=True,
    resources={r"/api/*": {"origins": ["http://localhost:8000", "http://127.0.0.1:8000"]}}, # Update for production
    allow_headers=["Content-Type", "Authorization"],
    methods=["GET", "POST", "OPTIONS"],
    expose_headers=["Content-Type"],
    max_age=3600
)

# Register API blueprint
app.register_blueprint(api_bp)


@app.route("/")
def hello_world():
    return render_template("index.html")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)