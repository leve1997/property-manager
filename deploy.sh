#!/bin/bash
set -e

cd "$(dirname "$0")"

git pull origin main
source .venv/bin/activate
pip install -r requirements.txt -q
sudo systemctl restart gunicorn

echo "Deployed successfully."
