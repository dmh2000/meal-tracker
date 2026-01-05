#!/usr/bin/env python3
"""Meal Tracker API Server."""

import argparse
import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from flask import Flask, request
from flask_cors import CORS

from database import init_db
from routes.auth_routes import auth_bp
from routes.food_routes import food_bp
from routes.meal_routes import meal_bp
from routes.log_routes import log_bp

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)


def create_app() -> Flask:
    """Create and configure the Flask application."""
    app = Flask(__name__)

    CORS(app, supports_credentials=True, origins=["http://localhost:5173", "http://localhost:5000"])

    init_db()

    # Request logging middleware
    @app.before_request
    def log_request():
        logger.info(f">>> {request.method} {request.path} from {request.remote_addr}")
        if request.content_type and 'json' in request.content_type:
            try:
                data = request.get_json(silent=True)
                if data:
                    # Don't log sensitive data
                    safe_data = {k: v for k, v in data.items() if k not in ['password']}
                    logger.info(f"    Request body: {safe_data}")
            except Exception:
                pass

    @app.after_request
    def log_response(response):
        logger.info(f"<<< {request.method} {request.path} -> {response.status_code}")
        return response

    app.register_blueprint(auth_bp)
    app.register_blueprint(food_bp)
    app.register_blueprint(meal_bp)
    app.register_blueprint(log_bp)

    @app.route("/api/health", methods=["GET"])
    def health():
        return {"status": "ok"}

    # Log registered routes
    logger.info("Registered routes:")
    for rule in app.url_map.iter_rules():
        methods = ','.join(sorted(rule.methods - {'HEAD', 'OPTIONS'}))
        if methods:
            logger.info(f"  {methods:20s} {rule.rule}")

    return app


def main():
    parser = argparse.ArgumentParser(description="Meal Tracker API Server")
    parser.add_argument("--port", type=int, default=5001, help="Port to listen on (default: 5001)")
    parser.add_argument("--host", type=str, default="127.0.0.1", help="Host to bind to (default: 127.0.0.1)")
    parser.add_argument("--debug", action="store_true", help="Enable debug mode")

    args = parser.parse_args()

    app = create_app()
    logger.info(f"Starting API server on http://{args.host}:{args.port}")
    app.run(host=args.host, port=args.port, debug=args.debug)


if __name__ == "__main__":
    main()
