""" Film Test interactions for API """
import datetime
from flask import jsonify, request, make_response
from flask_api import status
from flask_login import current_user
from sqlalchemy.sql import text
from sqlalchemy.exc import IntegrityError

from filmlog.functions import next_id, zero_to_none, key_or_none, \
                              time_to_seconds, log

def get_all_tests(connection):
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

def get_all_test_curves(connection):
    """ charts.js friendly data output of film test curves """
    userID = current_user.get_id()
    qry = text("""SELECT FilmTests.filmTestID,
    FilmTypes.filmTypeID AS filmTypeID,
    FilmTypes.name AS filmName, FilmTypes.iso,
    CONV(displayColor, 10, 16) AS displayColor
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
            "displayColor" : "#" + row['displayColor'].zfill(6),
            "steps" : steps
        }
        filmTests['data'].append(film)

    return jsonify(filmTests), status.HTTP_200_OK

def get_tests(connection, filmTypeID):
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

def get_test(connection, filmTypeID, filmTestID):
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
    AND FilmTests.filmTestID = :filmTestID""")
    films_query = connection.execute(qry,
        userID=userID,
        filmTypeID=filmTypeID,
        filmTestID=filmTestID).fetchone()

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
        }
    }
    return jsonify(filmTest), status.HTTP_200_OK

def get_test_results(connection, filmTypeID, filmTestID):
    """ Get film test results (dmax, CI, etc.)"""
    userID = current_user.get_id()

    qry = text("""SELECT filmTestID, baseFog, dMax, gamma,
        contrastIndex, kodakISO
        FROM FilmTests
        JOIN FilmTypes ON FilmTypes.userID = FilmTests.userID
            AND FilmTypes.filmTypeID = FilmTests.filmTypeID
        WHERE FilmTests.userID = :userID
        AND FilmTests.filmTypeID = :filmTypeID
        AND FilmTests.filmTestID = :filmTestID""")
    films_query = connection.execute(qry,
        userID=userID,
        filmTypeID=filmTypeID,
        filmTestID=filmTestID).fetchone()

    filmTest = {
        "data" : {
            "id" : films_query['filmTestID'],
            "filmTestID" : films_query['filmTestID'],
            "kodakISO" : films_query['kodakISO'],
            "baseFog" : float(films_query['baseFog']) if films_query['baseFog'] else None,
            "dMax" : float(films_query['dMax']) if films_query['dMax'] else None,
            "gamma" : float(films_query['gamma']) if films_query['gamma'] else None,
            "contrastIndex" : float(films_query['contrastIndex'])
                if films_query['contrastIndex'] else None,
        }
    }
    return jsonify(filmTest), status.HTTP_200_OK

def update_test_results(connection, filmTypeID, filmTestID):
    """ Update film test results (dmax, CI, etc.)"""
    userID = current_user.get_id()
    json = request.get_json()

    qry = text("""UPDATE FilmTests
        SET baseFog = :baseFog, dMax = :dMax, gamma = :gamma,
        contrastIndex = :contrastIndex, kodakISO = :kodakISO
        WHERE FilmTests.userID = :userID
        AND FilmTests.filmTypeID = :filmTypeID
        AND FilmTests.filmTestID = :filmTestID""")

    try:
        connection.execute(qry,
            userID=userID,
            filmTypeID=filmTypeID,
            filmTestID=filmTestID,
            baseFog=key_or_none(json, 'baseFog'),
            dMax=key_or_none(json, 'dMax'),
            gamma=key_or_none(json, 'gamma'),
            contrastIndex=key_or_none(json, 'contrastIndex'),
            kodakISO=key_or_none(json, 'kodakISO'))
    except IntegrityError:
        return "FAILED", status.HTTP_409_CONFLICT
    resp = make_response(jsonify(json))
    return resp, status.HTTP_204_NO_CONTENT

# pylint: disable=pointless-string-statement
""" This is split out as it makes interacting with the steps easier
    in JavaScript without having to re-request the bulk of the test data """
def get_test_steps(connection, filmTestID):
    """ Get specific film test steps """
    userID = current_user.get_id()

    qry = text("""SELECT stepNumber, stepDensity, logE, filmDensity
        FROM FilmTestStepsView
        WHERE userID = :userID
        AND filmTestID = :filmTestID""")
    steps_query = connection.execute(qry,
        userID=userID,
        filmTestID=filmTestID)

    steps = {
        "data": []
    }

    for row in steps_query:
        step = {
            "stepNumber": row['stepNumber'],
            "stepDensity":float(row['stepDensity']),
            "logE": float(row['logE']),
            "filmDensity": float(row['filmDensity']),
        }
        steps['data'].append(step)
    return jsonify(steps), status.HTTP_200_OK

def add_test(connection, filmTypeID):
    """ Add a new film test """
    userID = current_user.get_id()
    json = request.get_json()
    nextFilmTestID = next_id(connection, 'filmTestID', 'FilmTests')

    qry = text("""INSERT INTO FilmTests
        (userID, filmTestID, filmTypeID, enlargerID, enlargerLensID, filterID,
         stepTabletID, headHeight, filmSize, lux, fstop, exposureTime,
         developer, devTime, devTemperature, prebath, stop, agitation,
         rotaryRPM, notes)
        VALUES (:userID, :filmTestID, :filmTypeID, :enlargerID, :enlargerLensID,
         :filterID, :stepTabletID, :headHeight, :filmSize, :lux, :fstop,
         :exposureTime, :developer, :devTime, :devTemperature,
         :prebath, :stop, :agitation, :rotaryRPM, :notes)""")
    try:
        connection.execute(qry,
                           userID=userID,
                           filmTestID=nextFilmTestID,
                           filmTypeID=filmTypeID,
                           enlargerID=json['data']['enlargerID'],
                           enlargerLensID=json['data']['enlargerLensID'],
                           filterID=json['data']['filterID'],
                           stepTabletID=json['data']['stepTabletID'],
                           headHeight=zero_to_none(json['data']['headHeight']),
                           filmSize=json['data']['filmSize'],
                           lux=json['data']['lux'],
                           fstop=json['data']['fstop'],
                           exposureTime=key_or_none(json, 'exposureTime'),
                           developer=json['data']['developer'],
                           devTime=time_to_seconds(json['data']['devTime']),
                           devTemperature=json['data']['devTemperature'],
                           prebath=json['data']['prebath'],
                           stop=json['data']['stop'],
                           agitation=json['data']['agitation'],
                           rotaryRPM=zero_to_none(json['data']['rotaryRPM']),
                           notes=json['data']['notes'])
    except IntegrityError:
        log("Failed to create new film test via API")
        return "FAILED", status.HTTP_409_CONFLICT
    json['data']['id'] = str(nextFilmTestID)
    json['data']['created_on'] = datetime.datetime.now()
    resp = make_response(jsonify(json))
    log("Created new film test via API")
    return resp, status.HTTP_201_CREATED

def update_test_steps(connection, filmTestID):
    """ Update specific film test steps """
    userID = current_user.get_id()
    json = request.get_json()

    qry = text("""REPLACE INTO FilmTestSteps
                (userID, filmTestID, stepNumber, filmDensity)
                VALUES (:userID, :filmTestID, :stepNumber, :filmDensity)""")

    try:
        for step in json['data']:
            if step['stepNumber'] > 0 and step['stepNumber'] <= 21:
                connection.execute(qry,
                                   userID=userID,
                                   filmTestID=filmTestID,
                                   stepNumber=step['stepNumber'],
                                   filmDensity=step['filmDensity'])
            else:
                raise IntegrityError
    except IntegrityError:
        return "FAILED", status.HTTP_409_CONFLICT
    resp = make_response(jsonify(json))
    return resp, status.HTTP_204_NO_CONTENT
