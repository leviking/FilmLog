#!/bin/bash
. venv/bin/activate
export FLASK_APP="filmlog"
export FLASK_DEBUG=1
#export DB_URL="mysql+mysqldb://tim:e9xlb18@192.168.100.2/FilmLogDev?charset=utf8"
#DB_URL="mysql+mysqldb://tim:e9xlb18@192.168.100.2/FilmLogDev?charset=utf8"
# cd filmlog
flask run --host=0.0.0.0
