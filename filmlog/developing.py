from flask import request, render_template, redirect, url_for, flash, abort
from sqlalchemy.sql import select, text, func
import os, re

from flask_login import LoginManager, login_required, current_user, login_user, UserMixin

from flask_wtf import FlaskForm
from wtforms import Form, StringField, DateField, SelectField, IntegerField, \
    TextAreaField, DecimalField, SelectMultipleField, BooleanField
from wtforms.validators import DataRequired, Optional, Length, NumberRange
from wtforms import widgets

from filmlog import app
from filmlog import database, engine
from filmlog import functions
from filmlog import files

class DeveloperForm(FlaskForm):
    name = StringField('Name',
        validators=[DataRequired(), Length(min=1, max=64)])
    mixedOn = DateField('Mixed On',
        validators=[Optional()])
    capacity = IntegerField('Capacity',
        validators=[NumberRange(min=0,max=65535),
                    DataRequired()])
    type = SelectField('Type',
        validators=[DataRequired()],
        choices=[('Black & White', 'Black & White'),('C-41', 'C-41'),('E-6', 'E-6'),('ECN2', 'ECN2')])
    kind = SelectField('Kind',
        validators=[DataRequired()],
        choices=[('One-Shot', 'One-Shot'),('Multi-Use', 'Multi-Use'),('Replenishment', 'Replenishment')])
    state = SelectField('State',
        validators=[DataRequired()],
        choices=[('Active', 'Active'),('Retired', 'Retired')])
    notes = TextAreaField('Notes',
        validators=[Optional()],
        filters = [lambda x: x or None])

class DeveloperLogForm(FlaskForm):
    loggedOn = DateField('Logged On',
        validators=[Optional()])
    mlReplaced = IntegerField('Replaced (ml)',
        validators=[NumberRange(min=0,max=65535),
                    Optional()])
    mlUsed = IntegerField('Used (ml)',
        validators=[NumberRange(min=0,max=65535),
                    Optional()])
    temperature = DecimalField('Temperature (C)', places=1,
        validators=[Optional()],
        filters = [lambda x: x or None])
    devTime = StringField('Development Time',
        validators=[Optional(), functions.validate_exposure_time])

@app.route('/developing', methods = ['GET', 'POST'])
@login_required
def developing():
    connection = engine.connect()
    transaction = connection.begin()
    userID = current_user.get_id()
    developer_form = DeveloperForm()

    if request.method == 'POST':
        if developer_form.validate_on_submit():
            nextDeveloperID = functions.next_id(connection, 'developerID', 'Developers')
            qry = text("""INSERT INTO Developers
                (userID, developerID, name, mixedOn, capacity, type, kind,
                state, notes)
                VALUES (:userID, :developerID, :name, :mixedOn,
                :capacity, :type, :kind, :state, :notes)""")
            functions.insert(connection, qry, "Developers",
                userID = userID,
                developerID = nextDeveloperID,
                name = developer_form.name.data,
                mixedOn = developer_form.mixedOn.data,
                capacity = developer_form.capacity.data,
                type = developer_form.type.data,
                kind = developer_form.kind.data,
                state = developer_form.state.data,
                notes = developer_form.notes.data)

    qry = text("""SELECT developerID, name, type, kind FROM Developers
        WHERE userID = :userID
        AND state = 'Active'""")
    active_developers = connection.execute(qry, userID = userID).fetchall()

    qry = text("""SELECT developerID, name, type, kind FROM Developers
        WHERE userID = :userID
        AND state = 'Retired'""")
    retired_developers = connection.execute(qry, userID = userID).fetchall()

    transaction.commit()
    return render_template('/developing/index.html',
        active_developers = active_developers,
        retired_developers = retired_developers,
        developer_form = developer_form)

@app.route('/developing/developer/<int:developerID>', methods = ['GET', 'POST'])
@login_required
def developer(developerID):
    connection = engine.connect()
    transaction = connection.begin()
    userID = current_user.get_id()
    developer_form = DeveloperForm()

    if request.method == 'POST':
        if request.form['button'] == 'retireDeveloper':
            qry = text("""UPDATE Developers
                SET state='Retired'
                WHERE userID = :userID
                AND developerID = :developerID""")
            connection.execute(qry,
                userID = userID,
                developerID = developerID)
        if request.form['button'] == 'unretireDeveloper':
            qry = text("""UPDATE Developers
                SET state='Active'
                WHERE userID = :userID
                AND developerID = :developerID""")
            connection.execute(qry,
                userID = userID,
                developerID = developerID)

    # Grab the main info for the developer
    qry = text("""SELECT developerID, name, mixedOn, capacity, type, kind,
        state, notes, DATEDIFF(NOW(), mixedOn) AS age
        FROM Developers
        WHERE userID = :userID
        AND developerID = :developerID""")
    developer_results = connection.execute(qry,
        userID = userID,
        developerID = developerID).fetchone()
    developer = dict(developer_results)

    # If it's a replenished developer, figure out how long it's been since
    # last replenishment
    if developer['kind'] == 'Replenishment':
        qry = text("""SELECT DATEDIFF(NOW(), loggedOn) AS last_replenished
            FROM DeveloperLogs
            WHERE userID = :userID
            AND developerID = :developerID
            AND mlReplaced != 0
            ORDER BY developerLogID LIMIT 1""")
        last_replenished = connection.execute(qry,
            userID = userID,
            developerID = developerID).fetchone()
        if not last_replenished:
            qry = text("""SELECT DATEDIFF(NOW(), mixedOn) AS last_replenished
                FROM Developers
                WHERE userID = :userID
                AND developerID = :developerID""")
            last_replenished = connection.execute(qry,
                userID = userID,
                developerID = developerID).fetchone()
        last_replenished_dict = dict(last_replenished)
        developer['last_replenished'] = last_replenished_dict['last_replenished']

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
    transaction.commit()
    return render_template('/developing/developer.html',
        developer = developer,
        developer_logs = developer_logs,
        film_stats = film_stats,
        developer_form = developer_form)
