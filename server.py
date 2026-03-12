import os
import requests
from flask import Flask

app = Flask(__name__)

GH_TOKEN = os.environ.get("GH_TOKEN")
GH_REPO  = "Alex-Azaroff/parking-bot-Don"

@app.route("/trigger")
def trigger():
    r = requests.post(
        f"https://api.github.com/repos/{GH_REPO}/actions/workflows/monitor.yml/dispatches",
        headers={
            "Authorization": f"token {GH_TOKEN}",
            "Accept": "application/vnd.github.v3+json"
        },
        json={"ref": "main"}
    )
    return f"Status: {r.status_code}", 200

@app.route("/")
def home():
    return "OK", 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)