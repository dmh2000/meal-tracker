#!/usr/bin/env python3
"""Meal Tracker API Server."""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from flask import Flask
from flask_cors import CORS

from database import init_db
from routes.auth_routes import auth_bp
from routes.food_routes import food_bp
from routes.meal_routes import meal_bp
from routes.log_routes import log_bp


def create_app() -> Flask:
    """Create and configure the Flask application."""
    app = Flask(__name__)

    CORS(app, supports_credentials=True, origins=["http://localhost:5173", "http://localhost:5000"])

    init_db()

    app.register_blueprint(auth_bp)
    app.register_blueprint(food_bp)
    app.register_blueprint(meal_bp)
    app.register_blueprint(log_bp)

    @app.route("/api/health", methods=["GET"])
    def health():
        return {"status": "ok"}

    return app


def main():
    parser = argparse.ArgumentParser(description="Meal Tracker API Server")
    parser.add_argument("--port", type=int, default=5001, help="Port to listen on (default: 5001)")
    parser.add_argument("--host", type=str, default="127.0.0.1", help="Host to bind to (default: 127.0.0.1)")
    parser.add_argument("--debug", action="store_true", help="Enable debug mode")

    args = parser.parse_args()

    app = create_app()
    print(f"Starting API server on http://{args.host}:{args.port}")
    app.run(host=args.host, port=args.port, debug=args.debug)


if __name__ == "__main__":
    main()
