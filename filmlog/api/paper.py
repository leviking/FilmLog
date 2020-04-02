""" Paper interactions for API """
from flask import jsonify, request, make_response
from flask_api import status
from flask_login import current_user
from sqlalchemy.sql import text
from sqlalchemy.exc import IntegrityError

from filmlog.functions import next_id, zero_to_none

## Films
def get_all(connection):
    """ Get all films of a project """
    userID = current_user.get_id()

    qry = text("""SELECT Papers.paperID, type, grade, surface, tone, name,
        COUNT(Prints.printID) AS prints
        FROM Papers
        LEFT OUTER JOIN Prints ON Prints.paperID = Papers.paperID
            AND Prints.userID = Papers.userID
        WHERE Papers.userID = :userID
        GROUP BY Papers.paperID
        ORDER BY name""")
    papers_query = connection.execute(qry,
                                      userID=userID).fetchall()

    papers = {
        "data": []
    }
    for row in papers_query:
        paper = {
            "id" : str(row['paperID']),
            "type" : row['type'],
            "grade" : row['grade'],
            "surface" : row['surface'],
            "tone" : row['tone'],
            "name" : row['name'],
            "prints" : row['prints'],
        }
        papers['data'].append(paper)
    return jsonify(papers), status.HTTP_200_OK
