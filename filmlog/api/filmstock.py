from flask_login import LoginManager, login_required, current_user, login_user, UserMixin
from flask import Blueprint, jsonify, request, make_response
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
            "id" : {
                "filmtype_id" : str(row['filmTypeID']),
                "filmsize_id": str(row['filmSizeID']),
            },
            "attributes" : {
                "brand" : row['brand'],
                "type" : row['type'],
                "iso" : row['iso'],
                "size" : row['size'],
                "qty" : row['qty'],
            }
        }
        filmstock["data"].append(item)
    return jsonify(filmstock), status.HTTP_200_OK
