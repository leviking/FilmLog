""" Binder interactions for API """
import datetime
from flask import jsonify, request, make_response
from flask_login import current_user
from flask_api import status
from sqlalchemy.sql import text
from sqlalchemy.exc import IntegrityError

from filmlog.functions import next_id, log

## Binders
def get_all(connection):
    """ Get all user's binders """
    userID = current_user.get_id()
    qry = text("""SELECT binderID, name, projectCount, createdOn
        FROM Binders WHERE userID = :userID""")
    binders_query = connection.execute(qry, userID=userID).fetchall()

    binders = {
        "data": []
    }
    for row in binders_query:
        binder = {
            "id" : str(row['binderID']),
            "name" : row['name'],
            "project_count" : row['projectCount'],
            "created_on" : row['createdOn']
        }
        binders["data"].append(binder)
    return jsonify(binders), status.HTTP_200_OK

def post(connection):
    """ Insert a new binder """
    userID = current_user.get_id()
    json = request.get_json()
    nextBinderID = next_id(connection, 'binderID', 'Binders')
    qry = text("""INSERT INTO Binders
        (binderID, userID, name, notes) VALUES (:binderID, :userID, :name, :notes)""")
    try:
        connection.execute(qry,
                           binderID=nextBinderID,
                           userID=userID,
                           name=json['data']['name'],
                           notes=json['data']['notes'])
    except IntegrityError:
        log("Failed to create new binder via API")
        return "FAILED", status.HTTP_409_CONFLICT
    json['data']['id'] = str(nextBinderID)
    json['data']['project_count'] = str(0)
    json['data']['created_on'] = datetime.datetime.now()
    resp = make_response(jsonify(json))
    log("Created new binder via API")
    return resp, status.HTTP_201_CREATED

## Binder (Singular)
def get(connection, binderID):
    """ Get a binder """
    userID = current_user.get_id()
    qry = text("""SELECT binderID, name, projectCount, createdOn, notes
        FROM Binders WHERE userID = :userID AND binderID = :binderID""")
    binder_query = connection.execute(qry,
                                      userID=userID,
                                      binderID=binderID).fetchone()
    binder = {
        "data" : {
            "type" : "binders",
            "id" : str(binderID),
            "name" : binder_query['name'],
            "project_count" : binder_query['projectCount'],
            "created_on" : binder_query['createdOn'],
            "notes" : binder_query['notes']
        }
    }
    return jsonify(binder), status.HTTP_200_OK

def patch(connection, binderID):
    """ Update a binder """
    userID = current_user.get_id()
    json = request.get_json()
    qry = text("""UPDATE Binders
                  SET name = :name,
                      notes = :notes
                  WHERE userID = :userID
                  AND binderID = :binderID""")
    try:
        connection.execute(qry,
                           name=json['data']['name'],
                           notes=json['data']['notes'],
                           userID=userID,
                           binderID=binderID)
    except IntegrityError:
        log("Failed to update binder via API")
        return "FAILED", status.HTTP_409_CONFLICT
    resp = make_response(jsonify(json))
    resp.headers['Location'] = "/binders/" + str(binderID)
    return resp, status.HTTP_204_NO_CONTENT

def delete(connection, binderID):
    """ Delete a binder """
    userID = current_user.get_id()
    qry = text("""DELETE FROM Binders WHERE userID = :userID AND binderID = :binderID""")
    try:
        connection.execute(qry,
                           binderID=binderID,
                           userID=userID)
    except IntegrityError:
        log("Failed to delete binder via API")
        return "FAILED", status.HTTP_403_FORBIDDEN
    log("Deleted binder via API")
    return "OK", status.HTTP_204_NO_CONTENT
