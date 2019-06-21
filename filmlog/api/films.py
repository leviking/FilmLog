""" Film interactions for API """
from flask import jsonify, request, make_response
from flask_api import status
from flask_login import current_user
from sqlalchemy.sql import text
from sqlalchemy.exc import IntegrityError

from filmlog.functions import next_id, zero_to_none

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

def post(connection, projectID):
    """ Add film """
    userID = current_user.get_id()
    json = request.get_json()
    nextFilmID = next_id(connection, 'filmID', 'Films')

    qry = text("""INSERT INTO Films (userID, filmID, projectID, cameraID,
        filmTypeID, filmSizeID, iso, fileDate, loaded,
        unloaded, developed, fileNo, title, development, notes)
        VALUES (:userID, :filmID, :projectID, :cameraID,
            :filmTypeID, :filmSizeID, :iso, :fileDate, :loaded,
            :unloaded, :developed, :fileNo, :title, :development, :notes)""")
    try:
        connection.execute(qry,
                           userID=userID,
                           filmID=nextFilmID,
                           projectID=projectID,
                           cameraID=zero_to_none(json['data']['cameraID']),
                           filmTypeID=zero_to_none(json['data']['filmTypeID']),
                           filmSizeID=json['data']['filmSizeID'],
                           iso=json['data']['shotISO'],
                           fileDate=json['data']['fileDate'],
                           loaded=json['data']['loaded'],
                           unloaded=json['data']['unloaded'],
                           developed=json['data']['developed'],
                           fileNo=json['data']['fileNo'],
                           title=json['data']['title'],
                           development=json['data']['development'],
                           notes=json['data']['notes'])
    except IntegrityError:
        return "FAILED", status.HTTP_409_CONFLICT
    json['data']['id'] = str(nextFilmID)
    resp = make_response(jsonify(json))
    return resp, status.HTTP_201_CREATED

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

## Get Film sizes
def get_film_sizes(connection):
    """ Get film sizes """

    qry = text("""SELECT filmSizeID, size, type, format FROM FilmSizes""")
    films_query = connection.execute(qry)
    film_sizes = {
        "data": []
    }
    for row in films_query:
        film = {
            "id" : row['filmSizeID'],
            "size" : row['size'],
            "type" : row['type'],
            "format" : row['format']
        }
        film_sizes['data'].append(film)
    return jsonify(film_sizes), status.HTTP_200_OK

# Get Public films
def get_film_list(connection):
    """ Get a list of all the available films """
    qry = text("""SELECT filmTypeID, brand, name, iso, kind
        FROM FilmTypes
        JOIN FilmBrands ON FilmBrands.filmBrandID = FilmTypes.filmBrandID
        ORDER BY brand, name, iso, kind""")
    films_query = connection.execute(qry).fetchall()

    films = {
        "data": []
    }
    for row in films_query:
        film = {
            "id" : row['filmTypeID'],
            "brand" : row['brand'],
            "name" : row['name'],
            "iso" : row['iso'],
            "kind" : row['kind'],
        }
        films['data'].append(film)
    return jsonify(films), status.HTTP_200_OK
