#!/usr/bin/env bash
set -e

./scripts/build.sh

# start the api server
pushd backend/api_server
python meals.py --host 127.0.0.1 --port 5001 &>../../log/api_server.log &
popd

# start the frontend server
pushd backend/web_server
python meals.py  --host 0.0.0.0 --port 5000 --static ../../frontend/dist --api-url http://127.0.0.1:5001 &>../../log/web_server.log &
popd



