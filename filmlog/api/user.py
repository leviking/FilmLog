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
