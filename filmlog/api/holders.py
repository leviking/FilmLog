""" Holder interactions for API """
from flask import jsonify, request, make_response
from flask_login import current_user
from flask_api import status
from sqlalchemy.sql import text
from sqlalchemy.exc import IntegrityError

from filmlog.functions import next_id

## Holders Stock
def get_all(connection):
    """ Get all user's (active) holders """
    userID = current_user.get_id()

    qry = text("""SELECT holderID, Holders.name, size,
        IF(exposed, "Exposed",
            IF(loaded, "Loaded", "Empty")) AS state,
        Holders.filmTypeID, Holders.iso, FilmTypes.name AS filmType,
        FilmTypes.iso AS filmISO
        FROM Holders
        LEFT OUTER JOIN FilmTypes ON FilmTypes.filmTypeID = Holders.filmTypeID
            AND FilmTypes.userID = Holders.userID
        WHERE Holders.userID = :userID
        AND Holders.status = 'Active' ORDER BY Holders.name""")
    holders = connection.execute(qry, userID=userID).fetchall()

    holders_json = {
        "data": []
    }
    for row in holders:
        if row['filmType']:
            film = row['filmType'] + ' ' + str(row['filmISO'])
        else:
            film = None
        item = {
            "id" : str(row['holderID']),
            "name" : row['name'],
            "size" : row['size'],
            "state" : row['state'],
            "film" : film
        }
        holders_json["data"].append(item)
    return jsonify(holders_json), status.HTTP_200_OK

def post(connection):
    """ Add holder """
    userID = current_user.get_id()
    json = request.get_json()
    nextHolderID = next_id(connection, 'holderID', 'Holders')
    qry = text("""INSERT INTO Holders (userID, holderID, name, size, notes)
        VALUES (:userID, :holderID, :name, :size, :notes)""")
    try:
        connection.execute(qry,
                           userID=userID,
                           holderID=nextHolderID,
                           name=json['data']['name'],
                           size=json['data']['size'],
                           notes=json['data']['notes'])
    except IntegrityError:
        return "FAILED", status.HTTP_409_CONFLICT
    json['data']['id'] = str(nextHolderID)
    resp = make_response(jsonify(json))
    return resp, status.HTTP_201_CREATED

def patch(connection, holderID):
    """ Update holder """
    userID = current_user.get_id()
    json = request.get_json()

    # Set holder states
    if json['action']:
        if json['action'] == 'Expose':
            qry = text("""UPDATE Holders SET exposed = NOW()
                WHERE userID = :userID AND holderID = :holderID""")
            try:
                connection.execute(qry, userID=userID, holderID=holderID)
            except IntegrityError:
                return "FAILED", status.HTTP_409_CONFLICT
        if json['action'] == 'Unload':
            qry = text("""UPDATE Holders
                SET loaded = NULL, exposed = NULL, unloaded = NOW()
                WHERE userID = :userID AND holderID = :holderID""")
            try:
                connection.execute(qry, userID=userID, holderID=holderID)
            except IntegrityError:
                return "FAILED", status.HTTP_409_CONFLICT
        if json['action'] == 'Reload':
            qry = text("""UPDATE Holders
                SET loaded = NOW(), exposed = NULL, unloaded = NULL
                WHERE userID = :userID AND holderID = :holderID""")
            try:
                connection.execute(qry, userID=userID, holderID=holderID)
            except IntegrityError:
                return "FAILED", status.HTTP_409_CONFLICT
        # If action is something else
        else:
            return "FAILED", status.HTTP_400_BAD_REQUEST
    # If we didn't get an action value at all
    else:
        return "FAILED", status.HTTP_400_BAD_REQUEST

    resp = make_response(jsonify(json))
    resp.headers['Location'] = "/holders/" + str(holderID)
    return resp, status.HTTP_204_NO_CONTENT
