from flask_login import LoginManager, login_required, current_user, login_user, UserMixin
from flask import Blueprint, jsonify, request, make_response
from sqlalchemy.sql import select, text, func
from sqlalchemy.exc import IntegrityError
from filmlog import database, functions
from flask_api import status
from filmlog import engine
from filmlog.functions import next_id


## Binders
def get_all(connection, transaction):
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

def post(connection, transaction):
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

## Binder (Singular)
def get(connection, transaction, binderID):
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

def patch(connection, transaction, binderID):
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

def delete(connection, transaction, binderID):
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
