#!/usr/bin/env python3
"""Meal Tracker Web Server - Serves static frontend files and proxies API requests."""

import argparse
import logging
from pathlib import Path

import requests
from flask import Flask, send_from_directory, send_file, request, Response

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)


def create_app(static_folder: str = "static", api_url: str = "http://localhost:5001") -> Flask:
    """Create and configure the Flask application."""
    app = Flask(__name__, static_folder=static_folder, static_url_path="")

    @app.route("/api/<path:path>", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
    def proxy_api(path):
        """Proxy all /api/* requests to the API server."""
        url = f"{api_url}/api/{path}"
        logger.info(f"Proxying {request.method} /api/{path} -> {url}")

        # Forward the request
        try:
            resp = requests.request(
                method=request.method,
                url=url,
                headers={k: v for k, v in request.headers if k.lower() not in ['host', 'content-length']},
                data=request.get_data(),
                cookies=request.cookies,
                allow_redirects=False
            )

            # Build response
            excluded_headers = ['content-encoding', 'content-length', 'transfer-encoding', 'connection']
            headers = [(k, v) for k, v in resp.raw.headers.items() if k.lower() not in excluded_headers]

            response = Response(resp.content, resp.status_code, headers)

            # Forward cookies from API server
            for cookie in resp.cookies:
                response.set_cookie(
                    cookie.name,
                    cookie.value,
                    httponly=cookie.has_nonstandard_attr('httponly'),
                    secure=cookie.secure,
                    samesite='Lax',
                    max_age=cookie.expires
                )

            logger.info(f"Proxy response: {resp.status_code}")
            return response

        except requests.exceptions.ConnectionError as e:
            logger.error(f"API server connection failed: {e}")
            return {"error": "API server unavailable"}, 503

    @app.route("/", defaults={"path": ""})
    @app.route("/<path:path>")
    def serve(path):
        """Serve static files or index.html for SPA routing."""
        static_path = Path(app.static_folder)

        # Don't serve index.html for /api routes (should be handled above)
        if path.startswith("api/"):
            logger.warning(f"Unhandled API route: {path}")
            return {"error": "Not found"}, 404

        if path and (static_path / path).exists():
            logger.info(f"Serving static file: {path}")
            return send_from_directory(app.static_folder, path)

        logger.info(f"Serving index.html for path: {path or '/'}")
        return send_file(static_path / "index.html")

    return app


def main():
    parser = argparse.ArgumentParser(description="Meal Tracker Web Server")
    parser.add_argument("--port", type=int, default=5000, help="Port to listen on (default: 5000)")
    parser.add_argument("--host", type=str, default="127.0.0.1", help="Host to bind to (default: 127.0.0.1)")
    parser.add_argument("--static", type=str, default="static", help="Static files directory (default: static)")
    parser.add_argument("--api-url", type=str, default="http://localhost:5001", help="API server URL (default: http://localhost:5001)")
    parser.add_argument("--debug", action="store_true", help="Enable debug mode")

    args = parser.parse_args()

    app = create_app(args.static, args.api_url)
    logger.info(f"Starting web server on http://{args.host}:{args.port}")
    logger.info(f"Serving static files from: {Path(args.static).absolute()}")
    logger.info(f"Proxying API requests to: {args.api_url}")
    app.run(host=args.host, port=args.port, debug=args.debug)


if __name__ == "__main__":
    main()
