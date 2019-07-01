""" Mixed Developers interactions for API """
from flask import jsonify, request, make_response
from flask_login import current_user
from flask_api import status
from sqlalchemy.sql import text
from sqlalchemy.exc import IntegrityError

from filmlog.functions import next_id, zero_to_none, \
                              time_to_seconds

## Developers
def get_all(connection):
    """ Get all user's mixed developers """
    userID = current_user.get_id()
    qry = text("""SELECT developerID, name, type, kind, state
        FROM Developers
        WHERE userID = :userID""")
    developer_query = connection.execute(qry, userID=userID).fetchall()

    developers = {
        "data": []
    }
    for row in developer_query:
        developer = {
            "id" : row['developerID'],
            "name" : row['name'],
            "type" : row['type'],
            "kind" : row['kind'],
            "state" : row['state'],
        }
        developers["data"].append(developer)
    return jsonify(developers), status.HTTP_200_OK

## Developer (Singular)
def get(connection, developerID):
    """ Get a developer """
    userID = current_user.get_id()
    qry = text("""SELECT developerID, name, mixedOn, type, kind, state,
        capacity, notes
        FROM Developers
        WHERE userID = :userID
        AND developerID = :developerID""")
    developer_query = connection.execute(qry,
                                         userID=userID,
                                         developerID=developerID).fetchone()

    developer = {
        "data" : {
            "id" : developer_query['developerID'],
            "name" : developer_query['name'],
            "mixed_on" : developer_query['mixedOn'],
            "type" : developer_query['type'],
            "kind" : developer_query['kind'],
            "state" : developer_query['state'],
            "capacity" : developer_query['capacity'],
            "notes" : developer_query['notes']
        }
    }
    return jsonify(developer), status.HTTP_200_OK
