#!/usr/bin/env bash
# Render build script.
# Configure this as the "Build Command" for your Render Web Service:
#   ./build.sh
# (Render will run `chmod +x build.sh` for you automatically, but if you
# ever run this locally on a fresh clone, run `chmod +x build.sh` first.)

set -o errexit  # exit immediately if a command fails

pip install --upgrade pip
pip install -r requirements.txt

python manage.py collectstatic --no-input
python manage.py migrate
