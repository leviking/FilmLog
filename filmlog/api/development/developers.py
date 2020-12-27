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
    remaining = None
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

    # If it's one-shot, figure out how much is left
    if developer_query['kind'] == 'One-Shot':
        qry = text("""SELECT capacity - SUM(mlUsed) AS remaining
            FROM DeveloperLogs
            JOIN Developers ON Developers.developerID = DeveloperLogs.developerID
            AND Developers.userID = DeveloperLogs.userID
            WHERE DeveloperLogs.userID = :userID
            AND DeveloperLogs.developerID = :developerID""")
        remaining_query = connection.execute(qry,
                                             userID=userID,
                                             developerID=developerID).fetchone()
        if remaining_query:
            remaining = round(remaining_query['remaining'])

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
            "remaining" : remaining,
            "notes" : developer_query['notes']
        }
    }
    return jsonify(developer), status.HTTP_200_OK

# Get logs of a particular mixed developer
def get_logs(connection, developerID, startDate=None, endDate=None):
    """ Get a developer's logs """
    userID = current_user.get_id()

    if not startDate:
        startDate = datetime.today() - timedelta(days=30)
    if not endDate:
        endDate = datetime.today()

    films_qry = text("""SELECT developerLogFilmID, size AS filmSize,
        FilmSizes.type AS filmSizeType, FilmSizes.format AS filmSizeFormat,
        FilmTypes.name AS filmName, iso, qty, compensation
        FROM DeveloperLogFilms
        LEFT OUTER JOIN FilmTypes On FilmTypes.filmTypeID = DeveloperLogFilms.filmTypeID
            AND FilmTypes.userID = DeveloperLogFilms.userID
        JOIN FilmSizes ON FilmSizes.filmSizeID = DeveloperLogFilms.filmSizeID
        WHERE DeveloperLogFilms.userID = :userID
        AND developerLogID = :developerLogID""")

    qry = text("""SELECT developerLogID, loggedOn, mlReplaced, mlUsed,
        temperature, notes,
        SECONDS_TO_DURATION(devTime) AS devTime
        FROM DeveloperLogs
        WHERE userID = :userID
        AND developerID = :developerID
        AND loggedOn >= :startDate
        AND loggedOn <= :endDate
        ORDER BY loggedOn DESC""")
    log_query = connection.execute(qry,
                                   userID=userID,
                                   developerID=developerID,
                                   startDate=startDate,
                                   endDate=endDate).fetchall()

    logs = {
        "data" : [],
        "pagination" : {
            "startDate" : startDate,
            "endDate" : endDate
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
                    "name" : film['filmName'],
                    "iso" : film['iso'],
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

# Grab some fun developer stats (mostly how many films have been developed)
def get_developer_stats(connection, developerID):
    """ Get film stats for a particular developer """
    userID = current_user.get_id()

    qry = text("""SELECT FilmTypes.name AS filmName, iso,
        size AS filmSize, SUM(qty) AS qty
        FROM DeveloperLogs
        JOIN DeveloperLogFilms ON DeveloperLogFilms.userID = DeveloperLogs.userID
            AND DeveloperLogFilms.developerLogID = DeveloperLogs.developerLogID
        LEFT OUTER JOIN FilmTypes On FilmTypes.filmTypeID = DeveloperLogFilms.filmTypeID
            AND FilmTypes.userID = DeveloperLogFilms.userID
        JOIN FilmSizes ON FilmSizes.filmSizeID = DeveloperLogFilms.filmSizeID
        WHERE DeveloperLogs.userID = :userID
        AND DeveloperLogs.developerID = :developerID
        GROUP BY DeveloperLogFilms.filmTypeID, DeveloperLogFilms.filmSizeID
        ORDER BY qty DESC""")
    films_developed_query = connection.execute(qry,
                                               userID=userID,
                                               developerID=developerID).fetchall()

    # Provide raw and offset count by film size. The offset is an adjustment
    # for Kodak's recommended 80 sq inches typically for replenishment.
    # For instance, it takes 4 4x5 sheets to equal 80 sq inches.
    qry = text("""SELECT size, SUM(qty) AS qty,
            CASE size
                WHEN '35mm 12' THEN SUM(qty) / (1/3)
                WHEN '35mm 24' THEN SUM(qty) / (2/3)
                WHEN '220' THEN SUM(qty) * 2
                WHEN '4x5' THEN SUM(qty) / 4
                WHEN '5x7' THEN SUM(qty) / (80/35)
                ELSE SUM(qty)
            END AS 'adjustedQty'
        FROM DeveloperLogs
        JOIN DeveloperLogFilms ON DeveloperLogFilms.userID = DeveloperLogs.userID
            AND DeveloperLogFilms.developerLogID = DeveloperLogs.developerLogID
        JOIN FilmSizes ON FilmSizes.filmSizeID = DeveloperLogFilms.filmSizeID
        WHERE DeveloperLogs.userID = :userID
        AND DeveloperLogs.developerID = :developerID
        GROUP BY DeveloperLogFilms.filmSizeID
        ORDER BY qty DESC""")
    film_qty_query = connection.execute(qry,
                                        userID=userID,
                                        developerID=developerID).fetchall()

    stats = {
        "data" : {},
    }

    films_developed = {
        "films" : [],
    }

    film_qty = {
        "sizes" : [],
    }

    for film_developed in films_developed_query:
        film = {
            "name" : film_developed['filmName'],
            "iso" : int(film_developed['iso']),
            "size" : film_developed['filmSize'],
            "qty" : int(film_developed['qty'])
        }
        films_developed['films'].append(film)

    for film_size in film_qty_query:
        size = {
            "size" : film_size['size'],
            "qty" : int(film_size['qty']),
            "adjusted_qty" : str(film_size['adjustedQty'])
        }
        film_qty['sizes'].append(size)

    stats['data'] = films_developed
    stats['data'].update(film_qty)

    return jsonify(stats), status.HTTP_200_OK
