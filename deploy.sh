#!/bin/bash
. venv/bin/activate
pip install -r requirements.txt
git pull && ./migrate.sh && sudo apachectl graceful
