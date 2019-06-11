#!/usr/bin/python
import sys
sys.path.insert(0,"/srv/filmlog")

activate_this = '/srv/filmlog/venv/bin/activate_this.py'
with open(activate_this) as file_:
    exec(file_.read(), dict(__file__=activate_this))
from filmlog import app as application
