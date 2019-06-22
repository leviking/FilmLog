""" Film interactions for API """
from flask import jsonify, request, make_response
from flask_api import status
from flask_login import current_user
from sqlalchemy.sql import text
from sqlalchemy.exc import IntegrityError

from filmlog.functions import next_id, zero_to_none

## Helper Functions
def auto_decrement_film_stock(connection, filmTypeID, filmSizeID):
    """ Blindly Decrement Film Stock. If the film does not exist, the UPDATE
        won't do anything. This is currently by design since if a user isn't
        tracking a particular film, no sense in cluttering up the Film Stock.
        We only want to decrement films that are being tracked. """
    userID = current_user.get_id()
    qry = text("""SELECT 1 FROM UserPreferences
        WHERE userID = :userID
        AND autoUpdateFilmStock = 'Yes'""")
    result = connection.execute(qry,
                                userID=userID).fetchone()
    if result:
        qry = text("""UPDATE FilmStock SET qty = qty - 1
            WHERE userID = :userID
            AND filmTypeID = :filmTypeID
            AND filmSizeID = :filmSizeID""")
        connection.execute(qry,
                           userID=userID,
                           filmTypeID=filmTypeID,
                           filmSizeID=filmSizeID)


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
            "iso" : row['iso'],
            "size" : row['size'],
            "exposures" : row['exposures'],
            "film_type" : {
                "brand" : row['filmBrand'],
                "film" : row['film'],
                "box_speed" : row['filmBoxSpeed'],
            },
            "composite_id" : {
                "binder_id" : binderID,
                "project_id" : projectID,
                "film_id": row['filmID'],
            }
        }
        films['data'].append(film)
    return jsonify(films), status.HTTP_200_OK

def get(connection, binderID, projectID, filmID):
    """ Get film """
    userID = current_user.get_id()

    qry = text("""SELECT title, fileNo, fileDate,
        Films.iso AS iso, brand AS filmBrand, FilmTypes.name AS film,
        FilmTypes.iso AS filmBoxSpeed, FilmSizes.size AS size, exposures,
        development, Cameras.cameraID, Cameras.name AS cameraName
        FROM Films
        LEFT OUTER JOIN FilmTypes ON FilmTypes.filmTypeID = Films.filmTypeID
        LEFT OUTER JOIN FilmBrands ON FilmBrands.filmBrandID = FilmTypes.filmBrandID
        LEFT OUTER JOIN Cameras ON Cameras.cameraID = Films.cameraID
                                AND Cameras.userID = Films.userID
        JOIN FilmSizes ON FilmSizes.filmSizeID = Films.filmSizeID
        WHERE filmID = :filmID AND Films.userID = :userID ORDER BY fileDate""")
    films_query = connection.execute(qry,
                                     filmID=filmID,
                                     userID=userID).fetchone()
    film = {
        "data": {
            "id" : filmID,
            "title" : films_query['title'],
            "file_no" : films_query['fileNo'],
            "file_date" : films_query['fileDate'],
            "iso" : films_query['iso'],
            "size" : films_query['size'],
            "exposures" : films_query['exposures'],
            "development" : films_query['development'],
            "film_type" : {
                "brand" : films_query['filmBrand'],
                "film" : films_query['film'],
                "box_speed" : films_query['filmBoxSpeed'],
            },
            "camera" : {
                "id" : films_query['cameraID'],
                "name" : films_query['cameraName'],
            },
            "composite_id" : {
                "binder_id" : binderID,
                "project_id" : projectID,
                "film_id": filmID,
            }
        }
    }
    return jsonify(film), status.HTTP_200_OK

def post(connection, projectID):
    """ Add film """
    userID = current_user.get_id()
    json = request.get_json()
    nextFilmID = next_id(connection, 'filmID', 'Films')

    filmTypeID = zero_to_none(json['data']['filmTypeID'])
    filmSizeID = json['data']['filmSizeID']

    if json['data']['fileDate']:
        fileDate = json['data']['fileDate']
    else:
        fileDate = None

    qry = text("""INSERT INTO Films (userID, filmID, projectID, cameraID,
        filmTypeID, filmSizeID, iso, fileDate, loaded,
        unloaded, developed, fileNo, title, development, notes)
        VALUES (:userID, :filmID, :projectID, :cameraID,
            :filmTypeID, :filmSizeID, :iso, :fileDate, :loaded,
            :unloaded, :developed, UPPER(:fileNo), :title, :development, :notes)""")
    try:
        connection.execute(qry,
                           userID=userID,
                           filmID=nextFilmID,
                           projectID=projectID,
                           cameraID=zero_to_none(json['data']['cameraID']),
                           filmTypeID=filmTypeID,
                           filmSizeID=filmSizeID,
                           iso=json['data']['shotISO'],
                           fileDate=fileDate,
                           loaded=json['data']['loaded'],
                           unloaded=json['data']['unloaded'],
                           developed=json['data']['developed'],
                           fileNo=json['data']['fileNo'],
                           title=json['data']['title'],
                           development=json['data']['development'],
                           notes=json['data']['notes'])
    except IntegrityError:
        return "FAILED", status.HTTP_409_CONFLICT

    # Decrement the logged film from the film stock if the film
    # type was provided and it is a roll film.
    # If it's sheet film, we decrement only when need sheets
    # are added.
    qry = text("""SELECT 1 FROM FilmSizes
        WHERE filmSizeID = :filmSizeID
        AND format = 'Roll'""")
    film_format = connection.execute(qry, filmSizeID=filmSizeID).fetchone()
    if film_format and filmTypeID:
        auto_decrement_film_stock(connection, filmTypeID, filmSizeID)

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