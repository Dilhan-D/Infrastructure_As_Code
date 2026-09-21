import os
import time
import psycopg2
from flask import Flask, render_template, request
from user_agents import parse

app = Flask(__name__)

DB_CONFIG = {
    "host": os.environ.get("POSTGRES_HOST", "db"),
    "port": os.environ.get("POSTGRES_PORT", "5432"),
    "user": os.environ.get("POSTGRES_USER"),
    "password": os.environ.get("POSTGRES_PASSWORD"),
    "dbname": os.environ.get("POSTGRES_DB"),
}


def get_connection():
    return psycopg2.connect(**DB_CONFIG)


def log_visit(request, response_time):
    try:
        conn = get_connection()
        cur = conn.cursor()
        ua_string = request.headers.get("User-Agent", "")
        ua = parse(ua_string)
        ip = request.headers.get("X-Forwarded-For", request.remote_addr)

        cur.execute(
            """
            INSERT INTO visitors
            (ip, country, city, browser, os, device, hostname, user_agent, referer, visit_date, response_time)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, NOW(), %s)
            """,
            (
                ip,
                "N/A",
                "N/A",
                ua.browser.family,
                ua.os.family,
                ua.device.family,
                request.host,
                ua_string,
                request.referrer,
                response_time,
            ),
        )
        conn.commit()
        cur.close()
        conn.close()
    except Exception as e:
        app.logger.error(f"Erreur log_visit: {e}")


@app.route("/")
def home():
    start = time.time()
    response_time = round(time.time() - start, 4)
    log_visit(request, response_time)
    return render_template("index.html", active="home")


@app.route("/marches")
def marches():
    start = time.time()
    response_time = round(time.time() - start, 4)
    log_visit(request, response_time)
    return render_template("marches.html", active="marches")


@app.route("/apropos")
def apropos():
    start = time.time()
    response_time = round(time.time() - start, 4)
    log_visit(request, response_time)
    return render_template("apropos.html", active="apropos")


@app.route("/contact")
def contact():
    start = time.time()
    response_time = round(time.time() - start, 4)
    log_visit(request, response_time)
    return render_template("contact.html", active="contact")


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    debug = os.environ.get("FLASK_DEBUG", "0") == "1"
    app.run(host="0.0.0.0", port=port, debug=debug)