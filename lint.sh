#!/bin/bash
. venv/bin/activate
export FLASK_APP="filmlog"
export FLASK_DEBUG=1
cd filmlog

pylint filmlog

