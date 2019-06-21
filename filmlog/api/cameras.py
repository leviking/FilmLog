""" Camera interactions for API """
from flask import jsonify, request
from flask_api import status
from flask_login import current_user
from sqlalchemy.sql import text
#from sqlalchemy.exc import IntegrityError

#from filmlog.functions import next_id


def get_all(connection):
    """ Get all cameras """
    userID = current_user.get_id()

    if request.args.get("status") == 'Active':
        qry = text("""SELECT cameraID, name
            FROM Cameras
            WHERE userID = :userID
            AND status = 'Active'""")
    else:
        qry = text("""SELECT cameraID, name
            FROM Cameras
            WHERE userID = :userID""")
    cameras_query = connection.execute(qry, userID=userID).fetchall()
    cameras = {
        "data": []
    }
    for row in cameras_query:
        camera = {
            "id" : row['cameraID'],
            "name" : row['name'],
        }
        cameras['data'].append(camera)

    return jsonify(cameras), status.HTTP_200_OK
