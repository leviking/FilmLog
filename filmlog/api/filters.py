""" Filter interactions for API """
from flask import jsonify
from flask_api import status
from flask_login import current_user
from sqlalchemy.sql import text

def get_all(connection):
    """ Get all filters """
    userID = current_user.get_id()

    qry = text("""SELECT filterID, name, code
                  FROM Filters
                  WHERE userID = :userID""")
    result = connection.execute(qry, userID=userID).fetchall()
    filters = {
        "data": []
    }
    for row in result:
        single_filter = {
            "id" : row['filterID'],
            "filterID" : row['filterID'],
            "name" : row['name'],
            "code" : row['code']
        }
        filters['data'].append(single_filter)

    return jsonify(filters), status.HTTP_200_OK
