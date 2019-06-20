""" Film interactions for API """
import datetime
from flask import jsonify, request, make_response
from flask_api import status
from flask_login import current_user
from sqlalchemy.sql import text
from sqlalchemy.exc import IntegrityError

from filmlog.functions import next_id

## Films
def get_all(connection, binderID, projectID):
    """ Get all films """
    userID = current_user.get_id()

    qry = text("""SELECT filmID, title, fileNo,
        Films.iso AS iso, brand AS filmBrand, FilmTypes.name AS film,
        FilmTypes.iso AS filmBoxSpeed, FilmSizes.size AS size, exposures
        FROM Films
        LEFT OUTER JOIN FilmTypes ON FilmTypes.filmTypeID = Films.filmTypeID
        LEFT OUTER JOIN FilmBrands ON FilmBrands.filmBrandID = FilmTypes.filmBrandID
        JOIN FilmSizes ON FilmSizes.filmSizeID = Films.filmSizeID
        WHERE projectID = :projectID AND Films.userID = :userID ORDER BY fileDate""")
    films_query = connection.execute(qry,
                                     projectID=projectID,
                                     userID=userID).fetchall()
    films = {
        "data": []
    }
    for row in films_query:
        film = {
            "id" : str(row['filmID']),
            "title" : row['title'],
            "file_no" : row['fileNo'],
            "brand" : row['filmBrand'],
            "film" : row['film'],
            "box_speed" : row['filmBoxSpeed'],
            "iso" : row['iso'],
            "size" : row['size'],
            "exposures" : row['exposures'],
            "composite_id" : {
                "binder_id" : binderID,
                "project_id" : projectID,
                "film_id": row['filmID'],
            }
        }
        films['data'].append(film)
    return jsonify(films), status.HTTP_200_OK

def delete(connection, filmID):
    """ Delete a film """
    userID = current_user.get_id()
    qry = text("""DELETE FROM Films
                  WHERE userID = :userID AND filmID = :filmID""")
    try:
        connection.execute(qry,
                           userID=userID,
                           filmID=filmID)
    except IntegrityError:
        return "FAILED", status.HTTP_403_FORBIDDEN
    return "OK", status.HTTP_204_NO_CONTENT
