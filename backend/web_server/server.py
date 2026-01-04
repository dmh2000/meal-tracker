#!/usr/bin/env python3
"""Meal Tracker Web Server - Serves static frontend files."""

import argparse
from pathlib import Path

from flask import Flask, send_from_directory, send_file


def create_app(static_folder: str = "static") -> Flask:
    """Create and configure the Flask application."""
    app = Flask(__name__, static_folder=static_folder, static_url_path="")

    @app.route("/", defaults={"path": ""})
    @app.route("/<path:path>")
    def serve(path):
        static_path = Path(app.static_folder)

        if path and (static_path / path).exists():
            return send_from_directory(app.static_folder, path)

        return send_file(static_path / "index.html")

    return app


def main():
    parser = argparse.ArgumentParser(description="Meal Tracker Web Server")
    parser.add_argument("--port", type=int, default=5000, help="Port to listen on (default: 5000)")
    parser.add_argument("--host", type=str, default="127.0.0.1", help="Host to bind to (default: 127.0.0.1)")
    parser.add_argument("--static", type=str, default="static", help="Static files directory (default: static)")
    parser.add_argument("--debug", action="store_true", help="Enable debug mode")

    args = parser.parse_args()

    app = create_app(args.static)
    print(f"Starting web server on http://{args.host}:{args.port}")
    print(f"Serving static files from: {Path(args.static).absolute()}")
    app.run(host=args.host, port=args.port, debug=args.debug)


if __name__ == "__main__":
    main()
