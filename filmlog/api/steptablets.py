""" Step Tablets for API """
import datetime
from flask import jsonify, request, make_response
from flask_api import status
from flask_login import current_user
from sqlalchemy.sql import text
from sqlalchemy.exc import IntegrityError

from filmlog.functions import next_id, zero_to_none, key_or_none, \
                              time_to_seconds, log

def get_step_tablets(connection):
    """ Get all user's step tablets """
    userID = current_user.get_id()
    qry = text("""SELECT stepTabletID, name, createdOn
                  FROM StepTablets
                  WHERE userID = :userID""")
    steps_query = connection.execute(qry,
                                     userID=userID).fetchall()

    stepTablets = {
        "data": []
    }

    for step in steps_query:
        step = {
            "id" : step['stepTabletID'],
            "stepTabletID" : step['stepTabletID'],
            "name" : step['name'],
            "createdOn" : step['createdOn'],
        }
        stepTablets['data'].append(step)
    return jsonify(stepTablets), status.HTTP_200_OK

def get_step_tablet(connection, stepTabletID):
    """ Get specific step tablet """
    userID = current_user.get_id()
    qry = text("""SELECT stepTabletID, name, createdOn
                  FROM StepTablets
                  WHERE userID = :userID
                  AND stepTabletID = :stepTabletID""")
    steps_query = connection.execute(qry,
                                     userID=userID,
                                     stepTabletID=stepTabletID).fetchone()

    stepTablet = {
        "data" : {
            "id" : stepTabletID,
            "stepTabletID" : stepTabletID,
            "name" : steps_query['name'],
            "createdOn" : steps_query['createdOn']
        }
    }
    return jsonify(stepTablet), status.HTTP_200_OK

def get_step_tablet_steps(connection, stepTabletID):
    """ Get specific step tablet """
    userID = current_user.get_id()
    qry = text("""SELECT stepNumber, stepDensity
                  FROM StepTabletSteps
                  WHERE userID = :userID
                  AND stepTabletID = :stepTabletID""")
    steps_query = connection.execute(qry,
                                     userID=userID,
                                     stepTabletID=stepTabletID).fetchall()
    steps = {
        "data": []
    }

    for step in steps_query:
        step = {
            "id" : step['stepNumber'],
            "stepNumber" : step['stepNumber'],
            "stepDensity" : float(step['stepDensity'])
        }
        steps['data'].append(step)
    print(steps)
    return jsonify(steps), status.HTTP_200_OK

def add_step_tablet(connection):
    """ Add a new step tablet """
    userID = current_user.get_id()
    json = request.get_json()
    nextStepTabletID = next_id(connection, 'stepTabletID', 'StepTablets')

    qry = text("""INSERT INTO StepTablets (userID, stepTabletID, name)
                  VALUES (:userID, :stepTabletID, :name)""")

    try:
        connection.execute(qry,
                           userID=userID,
                           stepTabletID=nextStepTabletID,
                           name=json['data']['name'])
    except IntegrityError as e:
        log("Failed to create new film test via API")
        print(e)
        return "FAILED", status.HTTP_409_CONFLICT
    json['data']['id'] = str(nextStepTabletID)
    json['data']['created_on'] = datetime.datetime.now()
    resp = make_response(jsonify(json))
    log("Created new step tablet via API")
    return resp, status.HTTP_201_CREATED

def update_step_tablet_steps(connection, stepTabletID):
    """ Update specific step tablet steps """
    userID = current_user.get_id()
    json = request.get_json()

    qry = text("""REPLACE INTO StepTabletSteps
                (userID, stepTabletID, stepNumber, stepDensity)
                VALUES (:userID, :stepTabletID, :stepNumber, :stepDensity)""")

    try:
        for step in json['data']:
            if step['stepNumber'] > 0 and step['stepNumber'] <= 21:
                connection.execute(qry,
                                   userID=userID,
                                   stepTabletID=stepTabletID,
                                   stepNumber=step['stepNumber'],
                                   stepDensity=step['stepDensity'])
            else:
                raise IntegrityError
    except IntegrityError:
        return "FAILED", status.HTTP_409_CONFLICT
    resp = make_response(jsonify(json))
    return resp, status.HTTP_204_NO_CONTENT

def delete_step_tablet(connection, stepTabletID):
    """ Delete a step tablet """
    userID = current_user.get_id()
    qry = text("""DELETE FROM StepTablets
        WHERE userID = :userID
        AND stepTabletID = :stepTabletID""")
    try:
        connection.execute(qry,
                           userID=userID,
                           stepTabletID=stepTabletID)
    except IntegrityError:
        return "FAILED", status.HTTP_403_FORBIDDEN
    return "OK", status.HTTP_204_NO_CONTENT
