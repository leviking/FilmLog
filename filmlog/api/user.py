""" User interactions for API """
from flask import jsonify, request
from flask_api import status
from flask_login import current_user
from sqlalchemy.sql import text

def get_preferences(connection):
    """ Get user preferences """
    userID = current_user.get_id()

    qry = text("""SELECT autoUpdateFilmStock
        FROM UserPreferences
        WHERE userID = :userID""")

    prefs_query = connection.execute(qry, userID=userID).fetchone()
    user_preferences = {
        "autoUpdateFilmStock" : prefs_query['autoUpdateFilmStock'],
    }
    return jsonify(user_preferences), status.HTTP_200_OK

def patch_preferences(connection):
    """ Update the Auto Update Film Stock setting.
        This decrements a chosen film as soon as that film is logged
        (if it is defined as an available stock)"""
    userID = current_user.get_id()

    json = request.get_json()
    data = json['data']

    if data['name'] == 'autoUpdateFilmStock':
        if data['value'] == 'Yes' or data['value'] == 'No':
            qry = text("""UPDATE UserPreferences SET autoUpdateFilmStock = :value
                WHERE userID = :userID""")
            connection.execute(qry, value=data['value'], userID=userID)
            return "OK", status.HTTP_200_OK
    return "FAILED", status.HTTP_400_BAD_REQUEST
