from flask_login import LoginManager, login_required, current_user, login_user, UserMixin
from sqlalchemy.sql import select, text, func
from filmlog import database, functions
from flask import Blueprint, jsonify
from filmlog.api import api_blueprint
from filmlog import engine

# http://jsonapi.org/format/

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
    binders_query = connection.execute(qry, userID = userID).fetchall()

    binders = {
        "data": []
    }
    for row in binders_query:
        binder = {
            "type" : "binder",
            "id" : row['binderID'],
            "name" : row['name'],
            "project_count" : row['projectCount'],
            "created_on" : row['createdOn']
        }
        binders["data"].append(binder)
    transaction.commit()
    return jsonify(binders)
