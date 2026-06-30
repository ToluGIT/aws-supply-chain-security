"""Minimal Flask app. The app itself is not the point — it is the artifact
the supply chain pipeline builds, signs, and attests. Kept tiny on purpose."""
from flask import Flask, jsonify

app = Flask(__name__)


@app.route("/")
def index():
    return jsonify(status="ok", service="scs-demo-app")


@app.route("/healthz")
def healthz():
    return jsonify(healthy=True)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
