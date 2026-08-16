from flask import Flask, render_template, jsonify, request
import os
import platform
import socket
from datetime import datetime

from services.market_data import create_market_provider

app = Flask(__name__)
provider = create_market_provider()


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
    default_symbols = [
        {"symbol": "SPY", "name": "S&P 500 ETF", "range": "1M"},
        {"symbol": "DIA", "name": "Dow Jones ETF", "range": "1M"},
        {"symbol": "QQQ", "name": "Nasdaq ETF", "range": "1M"},
        {"symbol": "AAPL", "name": "Apple", "range": "1M"},
        {"symbol": "MSFT", "name": "Microsoft", "range": "1M"},
    ]
    return render_template("marches.html", active="marches", default_symbols=default_symbols)


@app.route("/apropos")
def apropos():
    return render_template("apropos.html", active="apropos")


@app.route("/contact")
def contact():
    return render_template("contact.html", active="contact")


@app.route("/api/markets/search")
def api_market_search():
    query = request.args.get("q", "").strip()
    if not query:
        return jsonify({"items": []})

    try:
        items = provider.search(query)
        return jsonify({"items": items})
    except Exception as exc:
        return jsonify({"items": [], "error": str(exc)}), 500


@app.route("/api/markets/quote/<symbol>")
def api_market_quote(symbol):
    try:
        item = provider.quote(symbol)
        return jsonify(item)
    except Exception as exc:
        return jsonify({"error": str(exc)}), 400


@app.route("/api/markets/history/<symbol>")
def api_market_history(symbol):
    range_name = request.args.get("range", "1M")
    interval = request.args.get("interval", "1D")
    try:
        data = provider.history(symbol, range_name=range_name, interval=interval)
        return jsonify(data)
    except Exception as exc:
        return jsonify({"error": str(exc), "symbol": symbol, "candles": []}), 400


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=int(os.getenv("PORT", "5000")),
        debug=os.getenv("FLASK_DEBUG", "0").lower() in {"1", "true", "yes"},
    )