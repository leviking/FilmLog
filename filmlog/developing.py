from flask import request, render_template, redirect, url_for, flash, abort
from sqlalchemy.sql import select, text, func
import os, re

from flask_login import LoginManager, login_required, current_user, login_user, UserMixin

from filmlog import app
from filmlog import database, engine
from filmlog import functions
from filmlog import files

@app.route('/developing/', methods = ['GET'])
@login_required
def developing():
    connection = engine.connect()
    userID = current_user.get_id()
    qry = text("""SELECT developerID, name FROM Developers
        WHERE userID = :userID
        AND state = 'Active'""")
    developers = connection.execute(qry, userID = userID).fetchall()
    return render_template('/developing/index.html',
        developers = developers)

@app.route('/developing/developer/<int:developerID>', methods = ['GET'])
@login_required
def developer(developerID):
    connection = engine.connect()
    userID = current_user.get_id()

    # Grab the main info for the developer
    qry = text("""SELECT developerID, name, mixedOn, replenishment,
        state, notes
        FROM Developers
        WHERE userID = :userID
        AND developerID = :developerID""")
    developer_results = connection.execute(qry,
        userID = userID,
        developerID = developerID).fetchone()
    developer = dict(developer_results)

    # Grab the logs
    qry = text("""SELECT developerLogID, loggedOn, mlReplaced,
        temperature, SECONDS_TO_DURATION(devTime) AS devTime, notes
        FROM DeveloperLogs
        WHERE userID = :userID
        AND developerID = :developerID
        ORDER BY loggedOn DESC""")
    developer_log_results = connection.execute(qry,
        userID = userID,
        developerID = developerID).fetchall()
    developer_logs = [{key: value for (key, value) in row.items()} for row in developer_log_results]

    # For each log entry we grab the films used and stuff them into the
    # data dictionary for teh logs. I feel like there is a cleaner way
    # but this works.
    qry = text("""SELECT developerLogFilmID, filmSize,
        DeveloperLogFilms.filmTypeID, FilmTypes.name AS filmName, iso,
        brand AS filmBrand, qty, compensation
        FROM DeveloperLogFilms
        JOIN FilmTypes On FilmTypes.filmTypeID = DeveloperLogFilms.filmTypeID
        JOIN FilmBrands On FilmBrands.filmBrandID = FilmTypes.filmBrandID
        WHERE userID = :userID
        AND developerLogID = :developerLogID""")

    for index, log in enumerate(developer_logs):
        films = connection.execute(qry,
            userID = userID,
            developerLogID = log['developerLogID']).fetchall()
        developer_logs[index]['films'] = films

    # Grab film statistics
    qry = text("""SELECT FilmTypes.name AS filmName, iso, brand AS filmBrand,
        filmSize, SUM(qty) AS qty
        FROM DeveloperLogs
        JOIN DeveloperLogFilms ON DeveloperLogFilms.userID = DeveloperLogs.userID
            AND DeveloperLogFilms.developerLogID = DeveloperLogs.developerLogID
        JOIN FilmTypes On FilmTypes.filmTypeID = DeveloperLogFilms.filmTypeID
        JOIN FilmBrands On FilmBrands.filmBrandID = FilmTypes.filmBrandID
        WHERE DeveloperLogs.userID = :userID
        AND DeveloperLogs.developerID = :developerID
        GROUP BY DeveloperLogFilms.filmTypeID
        ORDER BY brand, filmName""")
    film_stats = connection.execute(qry,
        userID = userID,
        developerID = developerID).fetchall()

    return render_template('/developing/developer.html',
        developer = developer,
        developer_logs = developer_logs,
        film_stats = film_stats)
