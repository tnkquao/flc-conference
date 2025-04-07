#!/usr/bin/env bash
# start.sh
gunicorn --bind 0.0.0.0:$PORT "app:create_app()"
