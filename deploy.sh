#!/bin/bash
. venv/bin/activate
git pull
pip install --upgrade -r requirements.txt
./migrate.sh 
sudo apachectl graceful
