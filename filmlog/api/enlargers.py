""" Enlarger interactions for API """
from flask import jsonify
from flask_api import status
from flask_login import current_user
from sqlalchemy.sql import text

def get_all(connection):
    """ Get all enlargers """
    userID = current_user.get_id()

    qry = text("""SELECT enlargerID, name
                  FROM Enlargers
                  WHERE userID = :userID""")
    result = connection.execute(qry, userID=userID).fetchall()
    enlargers = {
        "data": []
    }
    for row in result:
        enlarger = {
            "id" : row['enlargerID'],
            "enlargerID" : row['enlargerID'],
            "name" : row['name'],
        }
        enlargers['data'].append(enlarger)

    return jsonify(enlargers), status.HTTP_200_OK

def get_all_lenses(connection):
    """ Get all enlarger lenses """
    userID = current_user.get_id()

    qry = text("""SELECT enlargerLensID, name
                  FROM EnlargerLenses
                  WHERE userID = :userID""")
    result = connection.execute(qry, userID=userID).fetchall()
    enlargerLenses = {
        "data": []
    }
    for row in result:
        lens = {
            "id" : row['enlargerLensID'],
            "enlargerID" : row['enlargerLensID'],
            "name" : row['name'],
        }
        enlargerLenses['data'].append(lens)

    return jsonify(enlargerLenses), status.HTTP_200_OK
