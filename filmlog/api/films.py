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
    """ Get all films of a project """
    userID = current_user.get_id()

    qry = text("""SELECT filmID, title, fileNo,
            Films.iso AS iso,
            IF(FilmTypes.name IS NOT NULL, FilmTypes.name,
                (SELECT IF(COUNT(DISTINCT(filmTypeID)) > 1, 'Multiple', NULL)
                FROM Exposures WHERE Exposures.filmID = Films.filmID
                AND Exposures.userID = Films.userID)) AS film,
            FilmTypes.iso AS filmBoxSpeed, FilmSizes.size AS size, exposures
            FROM Films
            LEFT OUTER JOIN FilmTypes ON FilmTypes.filmTypeID = Films.filmTypeID
                AND FilmTypes.userID = Films.userID
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
    """ Get film from project """
    userID = current_user.get_id()

    qry = text("""SELECT title, fileNo, fileDate,
        Films.iso AS iso, FilmTypes.name AS film,
        FilmTypes.iso AS filmBoxSpeed, FilmSizes.size AS size, exposures,
        development, Cameras.cameraID, Cameras.name AS cameraName,
        loaded, unloaded, developed
        FROM Films
        LEFT OUTER JOIN FilmTypes ON FilmTypes.filmTypeID = Films.filmTypeID
            AND FilmTypes.userID = Films.userID
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
            "loaded" : films_query['loaded'],
            "unloaded" : films_query['unloaded'],
            "developed" : films_query['developed'],
            "film_type" : {
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
    # If it's sheet film, we decrement only when sheets are added.
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

# Get Users Film Types
def get_film_types(connection):
    """ Get a list of all the user's films """
    userID = current_user.get_id()
    qry = text("""SELECT FilmTypes.filmTypeID, name, FilmTypes.iso, kind,
        COUNT(Films.filmID) AS filmCount
        FROM FilmTypes
        LEFT OUTER JOIN Films ON Films.filmTypeID = FilmTypes.filmTypeID
            AND Films.userID = FilmTypes.userID
        WHERE FilmTypes.userID = :userID
        GROUP BY FilmTypes.filmTypeID
        ORDER BY name, iso, kind, filmCount""")
    films_query = connection.execute(qry, userID=userID).fetchall()

    films = {
        "data": []
    }
    for row in films_query:
        film = {
            "id" : row['filmTypeID'],
            "filmTypeID" : row['filmTypeID'],
            "name" : row['name'],
            "iso" : row['iso'],
            "kind" : row['kind'],
            "count" : row['filmCount']
        }
        films['data'].append(film)
    return jsonify(films), status.HTTP_200_OK

def get_film_type(connection, filmTypeID):
    """ Get film type details """
    userID = current_user.get_id()
    qry = text("""SELECT FilmTypes.filmTypeID, name, FilmTypes.iso, kind,
        COUNT(Films.filmID) AS filmCount
        FROM FilmTypes
        LEFT OUTER JOIN Films ON Films.filmTypeID = FilmTypes.filmTypeID
            AND Films.userID = FilmTypes.userID
        WHERE FilmTypes.userID = :userID
        AND FilmTypes.filmTypeID = :filmTypeID
        GROUP BY FilmTypes.filmTypeID""")
    film_query = connection.execute(qry,
        userID=userID,
        filmTypeID=filmTypeID).fetchone()

    film = {
        "data" : {
            "id" : film_query['filmTypeID'],
            "filmTypeID" : film_query['filmTypeID'],
            "name" : film_query['name'],
            "iso" : film_query['iso'],
            "kind" : film_query['kind'],
            "count" : film_query['filmCount']
        }
    }

    return jsonify(film), status.HTTP_200_OK

def delete_film_type(connection, filmTypeID):
    """ Delete a film type """
    userID = current_user.get_id()
    qry = text("""DELETE FROM FilmTypes
                  WHERE userID = :userID AND filmTypeID = :filmTypeID""")
    try:
        connection.execute(qry,
                           userID=userID,
                           filmTypeID=filmTypeID)
    except IntegrityError:
        return "FAILED", status.HTTP_403_FORBIDDEN
    return "OK", status.HTTP_204_NO_CONTENT

def add_film_type(connection):
    """ Add film type """
    userID = current_user.get_id()
    json = request.get_json()
    nextFilmTypeID = next_id(connection, 'filmTypeID', 'FilmTypes')

    if int(json['data']['iso']) < 0:
        return "FAILED", status.HTTP_400_BAD_REQUEST

    qry = text("""INSERT INTO FilmTypes (userID, filmTypeID, name, iso, kind)
        VALUES (:userID, :filmTypeID, :name, :iso, :kind)""")
    try:
        connection.execute(qry,
                           userID=userID,
                           filmTypeID=nextFilmTypeID,
                           name=zero_to_none(json['data']['name']),
                           iso=zero_to_none(json['data']['iso']),
                           kind=zero_to_none(json['data']['kind']))
    except IntegrityError:
        return "FAILED", status.HTTP_409_CONFLICT

    json['data']['id'] = str(nextFilmTypeID)
    resp = make_response(jsonify(json))
    return resp, status.HTTP_201_CREATED

def get_all_film_tests(connection):
    """ Get all film tests """
    userID = current_user.get_id()
    qry = text("""SELECT FilmTests.filmTestID,
    FilmTypes.filmTypeID AS filmTypeID,
    testedOn, FilmTypes.name AS filmName, FilmTypes.iso,
    kodakISO, developer, SECONDS_TO_DURATION(devTime) AS devTime,
    filmSize, baseFog, dMax, gamma, contrastIndex
    FROM FilmTests
    JOIN FilmTypes ON FilmTypes.userID = FilmTests.userID
        AND FilmTypes.filmTypeID = FilmTests.filmTypeID
    WHERE FilmTests.userID = :userID
    ORDER BY filmName, iso, devTime""")
    films_query = connection.execute(qry,
        userID=userID).fetchall()

    filmTests = {
        "data": []
    }

    for row in films_query:
        film = {
            "id" : row['filmTestID'],
            "filmTestID" : row['filmTestID'],
            "filmTypeID" : row['filmTypeID'],
            "testedOn" : row['testedOn'],
            "filmName" : row['filmName'],
            "iso" : row['iso'],
            "kodakISO" : row['kodakISO'],
            "developer": row['developer'],
            "devTime" : row['devTime'],
            "filmSize" : row['filmSize'],
            "baseFog" : float(row['baseFog']) if row['baseFog'] else None,
            "dMax" : float(row['dMax']) if row['dMax'] else None,
            "gamma" : float(row['gamma']) if row['gamma'] else None,
            "contrastIndex" : float(row['contrastIndex']) if row['contrastIndex'] else None
        }
        filmTests['data'].append(film)
    return jsonify(filmTests), status.HTTP_200_OK

def get_all_film_test_curves(connection):
    """ charts.js friendly data output of film test curves """
    userID = current_user.get_id()
    qry = text("""SELECT FilmTests.filmTestID,
    FilmTypes.filmTypeID AS filmTypeID,
    FilmTypes.name AS filmName, FilmTypes.iso
    FROM FilmTests
    JOIN FilmTypes ON FilmTypes.userID = FilmTests.userID
        AND FilmTypes.filmTypeID = FilmTests.filmTypeID
    WHERE FilmTests.userID = :userID
    AND FilmTests.graph = 'Yes'""")
    films_query = connection.execute(qry,
        userID=userID).fetchall()

    filmTests = {
        "data": []
    }

    for row in films_query:
        qry = text("""SELECT stepNumber, logE, filmDensity
            FROM FilmTestStepsView WHERE filmTestID = :filmTestID""")
        steps_query = connection.execute(qry,
                                         userID=userID,
                                         filmTestID=row['filmTestID']).fetchall()
        steps = []
        for step in steps_query:
            step = {
                "stepNumber": step['stepNumber'],
                "logE": float(step['logE']),
                "filmDensity": float(step['filmDensity']),
            }
            steps.append(step)

        film = {
            "id" : row['filmTestID'],
            "filmTestID" : row['filmTestID'],
            "filmTypeID" : row['filmTypeID'],
            "filmName" : row['filmName'],
            "iso" : row['iso'],
            "steps" : steps
        }
        filmTests['data'].append(film)

    return jsonify(filmTests), status.HTTP_200_OK

def get_film_tests(connection, filmTypeID):
    """ Get all tests for a film """
    userID = current_user.get_id()
    qry = text("""SELECT FilmTests.filmTestID,
    FilmTypes.filmTypeID AS filmTypeID, testedOn,
    FilmTypes.name AS filmName, FilmTypes.iso,
    kodakISO, developer, SECONDS_TO_DURATION(devTime) AS devTime,
    filmSize, baseFog, dMax, gamma, contrastIndex
    FROM FilmTests
    JOIN FilmTypes ON FilmTypes.userID = FilmTests.userID
        AND FilmTypes.filmTypeID = FilmTests.filmTypeID
    WHERE FilmTests.userID = :userID
    AND FilmTests.filmTypeID = :filmTypeID
    ORDER BY filmName, iso, devTime""")
    films_query = connection.execute(qry,
        userID=userID,
        filmTypeID=filmTypeID).fetchall()

    filmTests = {
        "data": []
    }

    for row in films_query:
        film = {
            "id" : row['filmTestID'],
            "filmTestID" : row['filmTestID'],
            "filmTypeID" : row['filmTypeID'],
            "testedOn" : row['testedOn'],
            "filmName" : row['filmName'],
            "iso" : row['iso'],
            "kodakISO" : row['kodakISO'],
            "developer": row['developer'],
            "devTime" : row['devTime'],
            "filmSize" : row['filmSize'],
            "baseFog" : float(row['baseFog']) if row['baseFog'] else None,
            "dMax" : float(row['dMax']) if row['dMax'] else None,
            "gamma" : float(row['gamma']) if row['gamma'] else None,
            "contrastIndex" : float(row['contrastIndex']) if row['contrastIndex'] else None
        }
        filmTests['data'].append(film)
    return jsonify(filmTests), status.HTTP_200_OK

def get_film_test(connection, filmTypeID, filmTestID):
    """ Get specific film test """
    userID = current_user.get_id()

    qry = text("""SELECT FilmTests.filmTestID,
    FilmTypes.name AS filmName, FilmTypes.iso, kodakISO,
    developer, SECONDS_TO_DURATION(devTime) AS devTime, testedOn,
    filmSize, baseFog, dMax, gamma, contrastIndex, notes
    FROM FilmTests
    JOIN FilmTypes ON FilmTypes.userID = FilmTests.userID
        AND FilmTypes.filmTypeID = FilmTests.filmTypeID
    WHERE FilmTests.userID = :userID
    AND FilmTests.filmTypeID = :filmTypeID
    AND FilmTests.filmTestID = :filmTestID
    ORDER BY filmName, iso, devTime""")
    films_query = connection.execute(qry,
        userID=userID,
        filmTypeID=filmTypeID,
        filmTestID=filmTestID).fetchone()

    qry = text("""SELECT stepNumber, stepDensity, logE, filmDensity
        FROM FilmTestStepsView WHERE filmTestID = :filmTestID""")
    steps_query = connection.execute(qry,
        userID=userID,
        filmTestID=filmTestID)

    steps = []
    for row in steps_query:
        step = {
            "stepNumber": row['stepNumber'],
            "stepDensity":float(row['stepDensity']),
            "logE": float(row['logE']),
            "filmDensity": float(row['filmDensity']),
        }
        steps.append(step)

    filmTest = {
        "data" : {
            "id" : films_query['filmTestID'],
            "filmTestID" : films_query['filmTestID'],
            "testedOn" : films_query['testedOn'],
            "filmName" : films_query['filmName'],
            "iso" : films_query['iso'],
            "kodakISO" : films_query['kodakISO'],
            "developer": films_query['developer'],
            "devTime" : films_query['devTime'],
            "filmSize" : films_query['filmSize'],
            "baseFog" : float(films_query['baseFog']) if films_query['baseFog'] else None,
            "dMax" : float(films_query['dMax']) if films_query['dMax'] else None,
            "gamma" : float(films_query['gamma']) if films_query['gamma'] else None,
            "contrastIndex" : float(films_query['contrastIndex'])
                if films_query['contrastIndex'] else None,
            "notes" : films_query['notes'],
            "steps": steps
        }
    }

    return jsonify(filmTest), status.HTTP_200_OK
