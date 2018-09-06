from flask_login import LoginManager, login_required, current_user, login_user, UserMixin
from flask import Blueprint, jsonify, request, make_response, url_for
from sqlalchemy.sql import select, text, func
from sqlalchemy.exc import IntegrityError
from filmlog import database, functions
from flask_api import status
from filmlog import engine
from filmlog.functions import next_id

## Film Stock
def get_all(connection, transaction):
    userID = current_user.get_id()

    qry = text("""SELECT FilmStock.filmTypeID AS filmTypeID,
        FilmStock.filmSizeID AS filmSizeID, FilmSizes.size AS size, qty,
        FilmBrands.brand AS brand, FilmTypes.name AS type, iso
        FROM FilmStock
        JOIN FilmTypes ON FilmTypes.filmTypeID = FilmStock.filmTypeID
        JOIN FilmBrands ON FilmBrands.filmBrandID = FilmTypes.filmBrandID
        JOIN FilmSizes ON FilmSizes.filmSizeID = FilmStock.filmSizeID
        WHERE userID = :userID
        ORDER BY size, brand, type, iso""")
    stock = connection.execute(qry, userID = userID).fetchall()

    filmstock = {
        "data": []
    }
    for row in stock:
        item = {
            "type" : "filmstock",
            "id" : str(row['filmTypeID']) + ':' + str(row['filmSizeID']),
            "attributes" : {
                "brand" : row['brand'],
                "type" : row['type'],
                "iso" : row['iso'],
                "size" : row['size'],
                "qty" : row['qty'],
                "composite_id" : {
                    "filmtype_id" : str(row['filmTypeID']),
                    "filmsize_id": str(row['filmSizeID'])
                }
            },
            "links" : {
                "self" : url_for("api.filmstock_details",
                    filmTypeID = row['filmTypeID'],
                    filmSizeID = row['filmSizeID'])
            }
        }
        filmstock["data"].append(item)
    return jsonify(filmstock), status.HTTP_200_OK

def get(connection, transaction, filmTypeID, filmSizeID):
    userID = current_user.get_id()

    qry = text("""SELECT FilmStock.filmTypeID AS filmTypeID,
        FilmStock.filmSizeID AS filmSizeID, FilmSizes.size AS size, qty,
        FilmBrands.brand AS brand, FilmTypes.name AS type, iso
        FROM FilmStock
        JOIN FilmTypes ON FilmTypes.filmTypeID = FilmStock.filmTypeID
        JOIN FilmBrands ON FilmBrands.filmBrandID = FilmTypes.filmBrandID
        JOIN FilmSizes ON FilmSizes.filmSizeID = FilmStock.filmSizeID
        WHERE userID = :userID
        AND FilmStock.filmTypeID = :filmTypeID
        AND FilmStock.filmSizeID = :filmSizeID""")
    stock = connection.execute(qry,
        userID = userID,
        filmTypeID = filmTypeID,
        filmSizeID = filmSizeID).fetchone()

    filmstock = {
        "data" : {
            "type" : "filmstock",
            "id" : str(filmTypeID) + ':' + str(filmSizeID),
            "attributes" : {
                "brand" : stock['brand'],
                "type" : stock['type'],
                "iso" : stock['iso'],
                "size" : stock['size'],
                "qty" : stock['qty'],
                "composite_id" : {
                    "filmtype_id" : str(filmTypeID),
                    "filmsize_id": str(filmSizeID)
                }
            },
            "links" : {
                "self" : url_for("api.filmstock_details",
                    filmTypeID = filmTypeID,
                    filmSizeID = filmSizeID)
            }
        }
    }
    return jsonify(filmstock), status.HTTP_200_OK

def patch(connection, transaction, filmTypeID, filmSizeID):
    userID = current_user.get_id()
    json = request.get_json()
    qry = text("""UPDATE FilmStock SET qty = :qty
        WHERE userID = :userID
        AND filmTypeID = :filmTypeID
        AND filmSizeID = :filmSizeID""")
    try:
        connection.execute(qry,
            qty = json['data']['attributes']['qty'],
            userID = userID,
            filmTypeID = filmTypeID,
            filmSizeID = filmSizeID)
    except IntegrityError:
       return "FAILED", status.HTTP_409_CONFLICT
    resp = make_response(jsonify(json))
    resp.headers['Location'] = "/filmstock/" + str(filmTypeID) + "/" + str(filmSizeID)
    return resp, status.HTTP_200_OK
