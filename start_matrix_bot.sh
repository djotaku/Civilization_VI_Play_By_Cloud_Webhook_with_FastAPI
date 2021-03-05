#!/usr/bin/env bash

echo "Start the virtual environment."
source venv/bin/activate

echo "Start the listener"
python -m civ_vi_webhook.services.matrix.matrix_bot_listener.py