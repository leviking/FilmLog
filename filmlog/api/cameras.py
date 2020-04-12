""" Camera interactions for API """
from flask import jsonify, request, make_response
from flask_api import status
from flask_login import current_user
from sqlalchemy.sql import text
from sqlalchemy.exc import IntegrityError

from filmlog.functions import next_id, zero_to_none

def get_all(connection):
    """ Get all cameras """
    userID = current_user.get_id()

    # There is a bit of code duplication here but it avoids having to generate
    # the query which could open up a SQL injection so it seems like it's
    # worth it.
    if request.args.get("status") == 'Active':
        qry = text("""SELECT cameraID, Cameras.name AS name, filmSize, status,
            FilmTypes.name AS loadedFilmName, FilmTypes.iso AS loadedFilmISO
            FROM Cameras
            LEFT OUTER JOIN FilmTypes ON FilmTypes.filmTypeID = Cameras.loadedFilmTypeID
                AND FilmTypes.userID = Cameras.userID
            WHERE Cameras.userID = :userID
            AND status = 'Active'
            ORDER BY Cameras.name""")
    else:
        qry = text("""SELECT cameraID, Cameras.name AS name, filmSize, status,
            FilmTypes.name AS loadedFilmName, FilmTypes.iso AS loadedFilmISO
            FROM Cameras
            LEFT OUTER JOIN FilmTypes ON FilmTypes.filmTypeID = Cameras.loadedFilmTypeID
                AND FilmTypes.userID = Cameras.userID
            WHERE Cameras.userID = :userID
            ORDER BY status, Cameras.name""")
    cameras_query = connection.execute(qry, userID=userID).fetchall()
    cameras = {
        "data": []
    }
    for row in cameras_query:
        camera = {
            "id" : row['cameraID'],
            "name" : row['name'],
            "status" : row['status'],
            "filmSize" : row['filmSize'],
            "loadedFilmName" : row['loadedFilmName'],
            "loadedFilmISO" : row['loadedFilmISO'],
        }
        cameras['data'].append(camera)

    return jsonify(cameras), status.HTTP_200_OK

def get(connection, cameraID):
    """ Get camera """
    userID = current_user.get_id()

    qry = text("""SELECT Lenses.lensID AS lensID, Lenses.name AS name
        FROM Lenses
        JOIN CameraLenses ON CameraLenses.userID = Lenses.userID
            AND CameraLenses.lensID = Lenses.lensID
        WHERE Lenses.userID = :userID
        AND CameraLenses.cameraID = :cameraID
        ORDER BY Lenses.name""")
    lenses_query = connection.execute(qry,
                                      userID=userID,
                                      cameraID=cameraID).fetchall()

    qry = text("""SELECT cameraID, filmSize, status, Cameras.name, notes, integratedShutter,
        FilmTypes.name AS loadedFilmName, FilmTypes.iso AS loadedFilmISO
        FROM Cameras
        LEFT OUTER JOIN FilmTypes ON FilmTypes.filmTypeID = Cameras.loadedFilmTypeID
            AND FilmTypes.userID = Cameras.userID
        WHERE cameraID = :cameraID AND Cameras.userID = :userID
        ORDER BY name""")
    camera_query = connection.execute(qry,
                                      cameraID=cameraID,
                                      userID=userID).fetchone()

    lenses = []
    for lens in lenses_query:
        lenses.append(
            {
                "id" : lens['lensID'],
                "name" : lens['name'],
            }
        )

    if camera_query['loadedFilmName']:
        filmLoaded = {
            "name" : camera_query['loadedFilmName'],
            "iso" : camera_query['loadedFilmISO'],
        }
    else:
        filmLoaded = None

    camera = {
        "data": {
            "id" : cameraID,
            "name" : camera_query['name'],
            "filmSize" : camera_query['filmSize'],
            "integratedShutter" : camera_query['integratedShutter'],
            "filmLoaded" : filmLoaded,
            "status" : camera_query['status'],
            "notes" : camera_query['notes'],
            "lenses" : lenses,
        }
    }

    if camera_query['integratedShutter'] == 'Yes':
        qry = text("""SELECT speed, measuredSpeed, idealSpeedMicroseconds,
            measuredSpeedMicroseconds, differenceStops
            FROM CameraShutterSpeeds
            WHERE userID = :userID
            AND cameraID = :cameraID""")
        shutter_query = connection.execute(qry,
                                           userID=userID,
                                           cameraID=cameraID).fetchall()
        shutter_speeds = []
        for shutter_speed in shutter_query:
            shutter_speeds.append(
                {
                    "speed" : shutter_speed['speed'],
                    "measuredSpeed" : shutter_speed['measuredSpeed'],
                    "idealSpeedMicroseconds" : shutter_speed['idealSpeedMicroseconds'],
                    "measuredSpeedMicroseconds" : shutter_speed['measuredSpeedMicroseconds'],
                    "differenceStops" : shutter_speed['differenceStops'],
                }
            )
        camera['data']['shutterSpeeds'] = shutter_speeds
    return jsonify(camera), status.HTTP_200_OK

def post(connection):
    """ Insert a new camera """
    userID = current_user.get_id()
    json = request.get_json()
    nextCameraID = next_id(connection, 'cameraID', 'Cameras')
    qry = text("""INSERT INTO Cameras
        (userID, cameraID, filmSize, integratedShutter, status, name, notes)
        VALUES (:userID, :cameraID, :filmSize, :integratedShutter, :status, :name, :notes)""")
    try:
        connection.execute(qry,
                           userID=userID,
                           cameraID=nextCameraID,
                           filmSize=json['data']['filmSize'],
                           integratedShutter=json['data']['integratedShutter'],
                           status=json['data']['status'],
                           name=json['data']['name'],
                           notes=json['data']['notes'])
    except IntegrityError:
        return "FAILED", status.HTTP_409_CONFLICT
    json['data']['id'] = str(nextCameraID)
    resp = make_response(jsonify(json))
    return resp, status.HTTP_201_CREATED

def loadFilm(connection, cameraID, filmTypeID):
    """ Load Film Into Camera"""
    userID = current_user.get_id()
    qry = text("""UPDATE Cameras
        SET loadedFilmTypeID = :filmTypeID
        WHERE Cameras.userID = :userID AND Cameras.cameraID = :cameraID""")
    try:
        connection.execute(qry,
                           filmTypeID=zero_to_none(filmTypeID),
                           userID=userID,
                           cameraID=cameraID)
    except IntegrityError:
        return "FAILED", status.HTTP_409_CONFLICT
    return "OK", status.HTTP_200_OK

def unloadFilm(connection, cameraID):
    """ Unload Film From Camera"""
    userID = current_user.get_id()
    qry = text("""UPDATE Cameras
        SET filmTypeID IS NULL
        WHERE Cameras.userID = :userID AND Cameras.camaerID = :cameraID""")
    try:
        connection.execute(qry,
                           userID=userID,
                           cameraID=cameraID)
    except IntegrityError:
        return "FAILED", status.HTTP_409_CONFLICT
    return "OK", status.HTTP_200_OK
