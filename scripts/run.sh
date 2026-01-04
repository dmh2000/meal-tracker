#!/usr/bin/env bash
set -e

./scripts/build.sh

# start the api server
pushd backend/api_server
gnome-terminal -- bash -c "python app.py --port 5001"
popd

# start the frontend server
pushd backend/web_server
gnome-terminal -- bash -c "python server.py --port 5000 --static ../../frontend/dist --api-url http://localhost:5001"
popd



