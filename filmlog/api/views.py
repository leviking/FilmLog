from flask_login import LoginManager, login_required, current_user, login_user, UserMixin
from sqlalchemy.sql import select, text, func
from filmlog import database, functions
from flask import Blueprint, jsonify, request
from filmlog.api import api_blueprint
from filmlog import engine

from filmlog.functions import next_id, insert

# http://jsonapi.org/format/

@api_blueprint.route('/',   methods = ['GET'])
def index():
    return "Hello"

@api_blueprint.route('/binders',  methods = ['GET', 'POST'])
@login_required
def binders():
    connection = engine.connect()
    transaction = connection.begin()
    userID = current_user.get_id()

    if request.method == 'POST':
        json = request.get_json()
        print json['data']['attributes']
        nextBinderID = next_id(connection, 'binderID', 'Binders')
        qry = text("""INSERT INTO Binders
            (binderID, userID, name) VALUES (:binderID, :userID, :name)""")
        insert(connection, qry,
            "Binder",
            binderID = nextBinderID,
            userID = userID,
            name = json['data']['attributes']['name'])

    qry = text("""SELECT binderID, name, projectCount, createdOn
        FROM Binders WHERE userID = :userID""")
    binders_query = connection.execute(qry, userID = userID).fetchall()

    binders = {
        "data": []
    }
    for row in binders_query:
        binder = {
            "type" : "binders",
            "id" : row['binderID'],
            "attributes" : {
                "name" : row['name'],
                "project_count" : row['projectCount'],
                "created_on" : row['createdOn']
            }
        }
        binders["data"].append(binder)
    transaction.commit()
    return jsonify(binders)

@api_blueprint.route('/binders/<int:binderID>/projects',  methods = ['GET'])
@login_required
def projects(binderID):
    connection = engine.connect()
    transaction = connection.begin()
    userID = current_user.get_id()

    qry = text("""SELECT projectID, name, filmCount, createdOn FROM Projects
        WHERE binderID = :binderID
        AND userID = :userID
        ORDER BY createdOn""")
    projects_query = connection.execute(qry, binderID=binderID, userID = userID).fetchall()

    projects = {
        "data": []
    }
    for row in projects_query:
        project = {
            "type" : "projects",
            "id" : {
                "binder_id" : binderID,
                "project_id": row['projectID'],
            },
            "attributes" : {
                "name" : row['name'],
                "film_count" : row['filmCount'],
                "created_on" : row['createdOn']
            }
        }
        projects["data"].append(project)
    transaction.commit()
    return jsonify(projects)


#@api_blueprint.route('/filmstock/<int:filmTypeID>/<int:filmSizeID>',  methods = ['PATCH', 'GET'])
#@login_required
#def binders():
    #connection = engine.connect()
    #transaction = connection.begin()
    #userID = current_user.get_id()

    #if request.method == 'PATCH':
