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
    qry = text("""SELECT developerID, name, mixedOn, replenishment,
        state, notes
        FROM Developers
        WHERE userID = :userID
        AND developerID = :developerID""")
    developer_results = connection.execute(qry,
        userID = userID,
        developerID = developerID).fetchone()
    developer = dict(developer_results)

    # For each developer log entry, grab the films
    # Will have to convert the developer logs to a dictionary of some sort?
    # (This is probably easy in an API where we can build a JSON structure)
    # E.g.:
    # d_dict = dict(developer)
    # d_dict['test'] = "bob"
    # So we'd assign, in the above ['test'] another dictionary or result set
    # so when we go to display it we can use a nested for (not efficient
    # but probably ok here)
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

    qry = text("""SELECT developerLogFilmID, filmSize,
        DeveloperLogFilms.filmTypeID, FilmTypes.name AS filmName, iso,
        brand AS filmBrand, qty, compensation
        FROM DeveloperLogFilms
        JOIN FilmTypes On FilmTypes.filmTypeID = DeveloperLogFilms.filmTypeID
        JOIN FilmBrands On FilmBrands.filmBrandID = FilmTypes.filmBrandID
        WHERE userID = :userID
        AND developerLogID = :developerLogID""")

    for index, log in enumerate(developer_logs):
        print index
        films = connection.execute(qry,
            userID = userID,
            developerLogID = log['developerLogID']).fetchall()
        developer_logs[index]['films'] = films
    print developer_logs

    return render_template('/developing/developer.html',
        developer = developer,
        developer_logs = developer_logs)
