""" Filmstock interactions for API """
from flask import jsonify, request, make_response
from flask_login import current_user
from flask_api import status
from sqlalchemy.sql import text
from sqlalchemy.exc import IntegrityError

## Film Stock
def get_all(connection):
    """ Get all films in stock """
    userID = current_user.get_id()

    qry = text("""SELECT FilmStock.filmTypeID AS filmTypeID,
        FilmStock.filmSizeID AS filmSizeID, FilmSizes.size AS size, qty,
        FilmTypes.name AS type, iso
        FROM FilmStock
        JOIN FilmTypes ON FilmTypes.filmTypeID = FilmStock.filmTypeID
            AND FilmTypes.userID = FilmStock.userID
        JOIN FilmSizes ON FilmSizes.filmSizeID = FilmStock.filmSizeID
        WHERE FilmStock.userID = :userID
        ORDER BY size, type, iso""")
    stock = connection.execute(qry, userID=userID).fetchall()

    filmstock = {
        "data": []
    }
    for row in stock:
        item = {
            "id" : str(row['filmTypeID']) + ':' + str(row['filmSizeID']),
            "type" : row['type'],
            "iso" : row['iso'],
            "size" : row['size'],
            "qty" : row['qty'],
            "composite_id" : {
                "filmtype_id" : str(row['filmTypeID']),
                "filmsize_id": str(row['filmSizeID'])
            }
        }
        filmstock["data"].append(item)
    return jsonify(filmstock), status.HTTP_200_OK

def get(connection, filmTypeID, filmSizeID):
    """ Get film from stock """
    userID = current_user.get_id()

    qry = text("""SELECT FilmStock.filmTypeID AS filmTypeID,
        FilmStock.filmSizeID AS filmSizeID, FilmSizes.size AS size, qty,
        FilmTypes.name AS type, iso
        FROM FilmStock
        JOIN FilmTypes ON FilmTypes.filmTypeID = FilmStock.filmTypeID
            FilmTypes.userID = FilmStock.userID
        JOIN FilmSizes ON FilmSizes.filmSizeID = FilmStock.filmSizeID
        WHERE FilmStock.userID = :userID
        AND FilmStock.filmTypeID = :filmTypeID
        AND FilmStock.filmSizeID = :filmSizeID""")
    stock = connection.execute(qry,
                               userID=userID,
                               filmTypeID=filmTypeID,
                               filmSizeID=filmSizeID).fetchone()

    filmstock = {
        "data" : {
            "id" : str(filmTypeID) + ':' + str(filmSizeID),
            "type" : stock['type'],
            "iso" : stock['iso'],
            "size" : stock['size'],
            "qty" : stock['qty'],
            "composite_id" : {
                "filmtype_id" : str(filmTypeID),
                "filmsize_id": str(filmSizeID)
            }
        }
    }
    return jsonify(filmstock), status.HTTP_200_OK

def patch(connection, filmTypeID, filmSizeID):
    """ Update film in stock """
    userID = current_user.get_id()
    json = request.get_json()
    if json['action']:
        if json['action'] == 'SetQTY':
            qry = text("""UPDATE FilmStock SET qty = :qty
                WHERE userID = :userID
                AND filmTypeID = :filmTypeID
                AND filmSizeID = :filmSizeID""")
            try:
                connection.execute(qry,
                                   qty=json['data']['qty'],
                                   userID=userID,
                                   filmTypeID=filmTypeID,
                                   filmSizeID=filmSizeID)
            except IntegrityError:
                return "FAILED", status.HTTP_409_CONFLICT
    resp = make_response(jsonify(json))
    resp.headers['Location'] = "/filmstock/" + str(filmTypeID) + "/" + str(filmSizeID)
    return resp, status.HTTP_200_OK

def delete(connection, filmTypeID, filmSizeID):
    """ Delete a film stock entirely """
    userID = current_user.get_id()
    qry = text("""DELETE FROM FilmStock
        WHERE userID = :userID
        AND filmTypeID = :filmTypeID
        AND filmSizeID = :filmSizeID""")
    connection.execute(qry,
                       userID=userID,
                       filmTypeID=filmTypeID,
                       filmSizeID=filmSizeID)
    return "OK", status.HTTP_200_OK
