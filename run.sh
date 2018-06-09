#!/bin/bash
. venv/bin/activate
export FLASK_APP="filmlog"
export FLASK_DEBUG=0
cd filmlog
flask run --host=0.0.0.0
