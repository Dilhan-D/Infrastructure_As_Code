from flask import Flask, render_template
import os
import platform
import socket
from datetime import datetime

app = Flask(__name__)


@app.route("/")
def home():
    hostname = socket.gethostname()
    nom = os.getenv("NOM", "Visiteur")
    environment = os.getenv("APP_ENV", "development")
    port = os.getenv("PORT", "5000")
    app_name = os.getenv("APP_NAME", "Application Flask")
    timestamp = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

    return render_template(
        "index.html",
        hostname=hostname,
        nom=nom,
        environment=environment,
        port=port,
        app_name=app_name,
        python_version=platform.python_version(),
        timestamp=timestamp,
        active="home",
    )


@app.route("/marches")
def marches():
    return render_template("marches.html", active="marches")


@app.route("/apropos")
def apropos():
    return render_template("apropos.html", active="apropos")


@app.route("/contact")
def contact():
    return render_template("contact.html", active="contact")


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=int(os.getenv("PORT", "5000")),
        debug=os.getenv("FLASK_DEBUG", "0").lower() in {"1", "true", "yes"},
    )