from flask import request, render_template, redirect, url_for, flash, abort
from sqlalchemy.sql import select, text, func
import os, re

from flask_login import LoginManager, login_required, current_user, login_user, UserMixin

from filmlog import app
from filmlog import database, engine
from filmlog import functions
from filmlog import files

@app.route('/developing/', methods = ['GET'])
@login_required
def developing():
    connection = engine.connect()
    userID = current_user.get_id()

    return render_template('/developing/index.html')
