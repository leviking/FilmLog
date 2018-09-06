from flask_login import LoginManager, login_required, current_user, login_user, UserMixin
from sqlalchemy.sql import select, text, func
from sqlalchemy.exc import IntegrityError
from filmlog import database, functions
from flask import Blueprint, jsonify, request, make_response
from flask_api import status
from filmlog.api import api_blueprint
from filmlog import engine
from filmlog.functions import next_id

# http://jsonapi.org/format/

@api_blueprint.route('/',   methods = ['GET'])
def index():
    return "Hello"

## Binders
def binders_get(connection, transaction):
    userID = current_user.get_id()
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
    return jsonify(binders)

def binders_post(connection, transaction):
    userID = current_user.get_id()
    json = request.get_json()
    nextBinderID = next_id(connection, 'binderID', 'Binders')
    qry = text("""INSERT INTO Binders
        (binderID, userID, name) VALUES (:binderID, :userID, :name)""")
    try:
        connection.execute(qry,
            binderID = nextBinderID,
            userID = userID,
            name = json['data']['attributes']['name'])
    except IntegrityError:
       return "FAILED", status.HTTP_409_CONFLICT
    json['data']['id'] = str(nextBinderID)
    json['data']['attributes']['projectCount'] = str(0)
    resp = make_response(jsonify(json))
    resp.headers['Location'] = "/binders/" + str(nextBinderID)
    return resp, status.HTTP_201_CREATED

@api_blueprint.route('/binders',  methods = ['GET', 'POST'])
@login_required
def binders():
    connection = engine.connect()
    transaction = connection.begin()
    userID = current_user.get_id()
    if request.method == 'GET':
        status = binders_get(connection, transaction)
    if request.method == 'POST':
        status = binders_post(connection, transaction)
    transaction.commit()
    return status


## Binder (Singular)
def binder_get(connection, transaction, binderID):
    userID = current_user.get_id()
    qry = text("""SELECT binderID, name, projectCount, createdOn
        FROM Binders WHERE userID = :userID AND binderID = :binderID""")
    binder_query = connection.execute(qry,
        userID = userID,
        binderID = binderID).fetchone()

    binder = {
        "data" : {
            "type" : "binders",
            "id" : binder_query['binderID'],
            "attributes" : {
                "name" : binder_query['name'],
                "project_count" : binder_query['projectCount'],
                "created_on" : binder_query['createdOn']
            }
        }
    }
    return jsonify(binder)

def binder_patch(connection, transaction, binderID):
    userID = current_user.get_id()
    json = request.get_json()
    qry = text("""UPDATE Binders SET name = :name
        WHERE userID = :userID AND binderID = :binderID""")
    try:
        connection.execute(qry,
            name = json['data']['attributes']['name'],
            userID = userID,
            binderID = binderID)
    except IntegrityError:
       return "FAILED", status.HTTP_409_CONFLICT
    resp = make_response(jsonify(json))
    resp.headers['Location'] = "/binders/" + str(binderID)
    return resp, status.HTTP_200_OK

def binder_delete(connection, transaction, binderID):
    userID = current_user.get_id()
    qry = text("""DELETE FROM Binders WHERE userID = :userID AND binderID = :binderID""")
    try:
        connection.execute(qry,
            binderID = binderID,
            userID = userID)
    except IntegrityError:
        transaction.rollback()
        return "FAILED", status.HTTP_403_FORBIDDEN
    return "OK", status.HTTP_204_NO_CONTENT

@api_blueprint.route('/binders/<int:binderID>',  methods = ['GET', 'PATCH', 'DELETE'])
@login_required
def binder(binderID):
    connection = engine.connect()
    transaction = connection.begin()
    if request.method == 'GET':
        status = binder_get(connection, transaction, binderID)
    if request.method == 'PATCH':
        status = binder_patch(connection, transaction, binderID)
    if request.method == 'DELETE':
        status = binder_delete(connection, transaction, binderID)
    transaction.commit()
    return status

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
