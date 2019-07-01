""" Mixed Developers interactions for API """
from datetime import datetime, timedelta
from flask import jsonify
from flask_login import current_user
from flask_api import status
from sqlalchemy.sql import text

## Developers
def get_all(connection):
    """ Get all user's mixed developers """
    userID = current_user.get_id()
    qry = text("""SELECT developerID, name, type, kind, state
        FROM Developers
        WHERE userID = :userID""")
    developer_query = connection.execute(qry, userID=userID).fetchall()

    developers = {
        "data": []
    }
    for dev in developer_query:
        developer = {
            "id" : dev['developerID'],
            "name" : dev['name'],
            "type" : dev['type'],
            "kind" : dev['kind'],
            "state" : dev['state'],
        }
        developers["data"].append(developer)
    return jsonify(developers), status.HTTP_200_OK

## Developer (Singular)
def get(connection, developerID):
    """ Get a developer """
    last_replenished = None
    userID = current_user.get_id()
    qry = text("""SELECT developerID, name, mixedOn, type, kind, state,
        capacity, notes
        FROM Developers
        WHERE userID = :userID
        AND developerID = :developerID""")
    developer_query = connection.execute(qry,
                                         userID=userID,
                                         developerID=developerID).fetchone()

    # If it's a replenished developer, figure out how long it's been since
    # last replenishment
    if developer_query['kind'] == 'Replenishment':
        qry = text("""SELECT DATEDIFF(NOW(), loggedOn) AS last_replenished
            FROM DeveloperLogs
            WHERE userID = :userID
            AND developerID = :developerID
            AND mlReplaced != 0
            ORDER BY developerLogID DESC LIMIT 1""")
        last_replenished_query = connection.execute(qry,
                                                    userID=userID,
                                                    developerID=developerID).fetchone()
        if last_replenished_query:
            last_replenished = last_replenished_query['last_replenished']

    qry = text("""SELECT DATEDIFF(NOW(), mixedOn) AS days_old
        FROM Developers
        WHERE userID = :userID
        AND developerID = :developerID""")
    days_old_query = connection.execute(qry,
                                        userID=userID,
                                        developerID=developerID).fetchone()
    days_old = days_old_query['days_old']

    developer = {
        "data" : {
            "id" : developer_query['developerID'],
            "name" : developer_query['name'],
            "mixed_on" : developer_query['mixedOn'],
            "type" : developer_query['type'],
            "kind" : developer_query['kind'],
            "state" : developer_query['state'],
            "capacity" : developer_query['capacity'],
            "days_old" : days_old,
            "last_replenished" : last_replenished,
            "notes" : developer_query['notes']
        }
    }
    return jsonify(developer), status.HTTP_200_OK

# Get logs of a particular mixed developer
def get_logs(connection, developerID, startDate=None):
    """ Get a developer's logs """
    userID = current_user.get_id()

    if not startDate:
        startDate = datetime.today() - timedelta(days=30)
    print(startDate)

    films_qry = text("""SELECT developerLogFilmID, size AS filmSize,
        FilmSizes.type AS filmSizeType, FilmSizes.format AS filmSizeFormat,
        FilmTypes.name AS filmName, iso, brand AS filmBrand, qty, compensation
        FROM DeveloperLogFilms
        LEFT OUTER JOIN FilmTypes On FilmTypes.filmTypeID = DeveloperLogFilms.filmTypeID
        LEFT OUTER JOIN FilmBrands On FilmBrands.filmBrandID = FilmTypes.filmBrandID
        JOIN FilmSizes ON FilmSizes.filmSizeID = DeveloperLogFilms.filmSizeID
        WHERE userID = :userID
        AND developerLogID = :developerLogID""")

    qry = text("""SELECT developerLogID, loggedOn, mlReplaced, mlUsed,
        temperature, devTime, notes
        FROM DeveloperLogs
        WHERE userID = :userID
        AND developerID = :developerID
        AND loggedOn > :startDate
        ORDER BY loggedOn DESC""")
    log_query = connection.execute(qry,
                                   userID=userID,
                                   developerID=developerID,
                                   startDate=startDate).fetchall()

    logs = {
        "data" : [],
        "pagination" : {
            "startDate" : startDate
        }
    }

    for log in log_query:
        films = []
        film_query = connection.execute(films_qry,
                                        userID=userID,
                                        developerLogID=log['developerLogID']).fetchall()
        for film in film_query:
            films.append(
                {
                    "id" : film['developerLogFilmID'],
                    "size" : film['filmSize'],
                    "type" : film['filmSizeType'],
                    "format" : film['filmSizeFormat'],
                    "brand" : film['filmBrand'],
                    "name" : film['filmName'],
                    "qty" : film['qty'],
                    "compensation" : film['compensation']
                }
            )

        logs['data'].append(
            {
                "id" : log['developerLogID'],
                "logged_on" : log['loggedOn'],
                "ml_replaced" : log['mlReplaced'],
                "ml_used" : log['mlUsed'],
                "temperature" : str(log['temperature']),
                "dev_time" : log['devTime'],
                "notes" : log['notes'],
                "films" : films,
            }
        )
    return jsonify(logs), status.HTTP_200_OK
