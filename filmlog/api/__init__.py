from flask import Blueprint
from flask_login import LoginManager, login_required, current_user, login_user, UserMixin

import json
from sqlalchemy.sql import select, text, func

from filmlog import database
engine = database.engine

api_blueprint = Blueprint('api', __name__)

@api_blueprint.route('/',   methods = ['GET'])
def index():
    return "Hello"

@api_blueprint.route('/binders',  methods = ['POST', 'GET'])
@login_required
def binders():
    connection = engine.connect()
    transaction = connection.begin()
    userID = current_user.get_id()

    qry = text("""SELECT binderID, name, projectCount, createdOn
        FROM Binders WHERE userID = :userID""")
    binders = connection.execute(qry, userID = userID).fetchall()
    transaction.commit()
    return "Here's a binder"
