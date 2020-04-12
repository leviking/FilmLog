""" Paper interactions for API """
from flask import jsonify, request, make_response
from flask_api import status
from flask_login import current_user
from sqlalchemy.sql import text
from sqlalchemy.exc import IntegrityError

from filmlog.functions import next_id

## Papers
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

def post(connection):
    """ Add paper """
    userID = current_user.get_id()
    json = request.get_json()
    nextPaperID = next_id(connection, 'paperID', 'Papers')

    qry = text("""INSERT INTO Papers (userID, paperID, type, grade, surface, tone, name)
        VALUES (:userID, :paperID, :type, :grade, :surface, :tone, :name)""")
    try:
        connection.execute(qry,
                           userID=userID,
                           paperID=nextPaperID,
                           type=json['data']['type'],
                           grade=json['data']['grade'],
                           surface=json['data']['surface'],
                           tone=json['data']['tone'],
                           name=json['data']['name'])
    except IntegrityError:
        return "FAILED", status.HTTP_409_CONFLICT
    json['data']['id'] = str(nextPaperID)
    resp = make_response(jsonify(json))
    return resp, status.HTTP_201_CREATED

def delete(connection, paperID):
    """ Delete paper """
    userID = current_user.get_id()
    qry = text("""DELETE FROM Papers
                  WHERE userID = :userID AND paperID = :paperID""")
    try:
        connection.execute(qry,
                           userID=userID,
                           paperID=paperID)
    except IntegrityError:
        return "FAILED", status.HTTP_403_FORBIDDEN
    return "OK", status.HTTP_204_NO_CONTENT
