#!/usr/bin/env bash

echo "Start the virtual environment."
source venv/bin/activate

# Defaults to port 8000
# with --port integer, can change the port number
echo "Start the server."
uvicorn civ_vi_webhook.main:app --port 5000 --reload