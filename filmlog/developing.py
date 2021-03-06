""" Developing specific views (/developing) """
from flask import request, render_template, redirect
from sqlalchemy.sql import text

from flask_login import login_required, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, DateField, DateTimeField, SelectField, \
    IntegerField, TextAreaField, DecimalField
from wtforms.validators import DataRequired, Optional, Length, NumberRange, \
    ValidationError

# Filmlog
from filmlog.config import app, engine
from filmlog import functions

class DeveloperForm(FlaskForm):
    """ Film Developer Form """
    name = StringField('Name',
                       validators=[DataRequired(),
                                   Length(min=1, max=64)])
    mixedOn = DateField('Mixed On',
                        validators=[Optional()])
    capacity = IntegerField('Capacity',
                            validators=[NumberRange(min=1, max=65535),
                                        DataRequired()])
    type = SelectField('Type',
                       validators=[DataRequired()],
                       choices=[('Black & White', 'Black & White'),
                                ('C-41', 'C-41'),
                                ('E-6', 'E-6'),
                                ('ECN2', 'ECN2')])
    kind = SelectField('Kind',
                       validators=[DataRequired()],
                       choices=[('One-Shot', 'One-Shot'),
                                ('Multi-Use', 'Multi-Use'),
                                ('Replenishment', 'Replenishment')])
    state = SelectField('State',
                        validators=[DataRequired()],
                        choices=[('Active', 'Active'),
                                 ('Retired', 'Retired')])
    notes = TextAreaField('Notes',
                          validators=[Optional()],
                          filters=[lambda x: x or None])

class DeveloperLogForm(FlaskForm):
    """ Form for updating a developer log entry """
    loggedOn = DateTimeField('Logged On',
                             validators=[Optional()])
    mlReplaced = IntegerField('Replaced (ml)',
                              validators=[NumberRange(min=1, max=65535),
                                          Optional()])
    mlUsed = IntegerField('Used (ml)',
                          validators=[NumberRange(min=1, max=65535),
                                      Optional()])
    temperature = DecimalField('Temperature (C)', places=1,
                               validators=[NumberRange(min=-100, max=200),
                                           Optional()],
                               filters=[lambda x: x or None])
    devTime = StringField('Development Time',
                          validators=[Optional(),
                                      functions.validate_exposure_time])
    notes = TextAreaField('Notes',
                          validators=[Optional()],
                          filters=[lambda x: x or None])

class DeveloperLogFilmForm(FlaskForm):
    """ Form for updating films associated with a developer log entry """
    filmSizeID = SelectField('Film Size',
                             validators=[DataRequired()],
                             coerce=int)
    filmTypeID = SelectField('Film',
                             validators=[Optional()],
                             coerce=int)
    qty = IntegerField('Qty',
                       validators=[NumberRange(min=1, max=255),
                                   DataRequired()])
    compensation = IntegerField('Compensation',
                                validators=[NumberRange(min=-100, max=100),
                                            Optional()])
    def populate_select_fields(self, connection):
        """ Helper function to populate select drop downs on the form """
        self.filmSizeID.choices = functions.get_film_sizes(connection)
        self.filmTypeID.choices = \
            functions.optional_choices("None",
                                       functions.get_film_types(connection))

@app.route('/developing', methods=['GET', 'POST'])
@login_required
def developing():
    """ Index page for developing section """
    connection = engine.connect()
    transaction = connection.begin()
    userID = current_user.get_id()
    developer_form = DeveloperForm()

    if request.method == 'POST':
        if developer_form.validate_on_submit():
            qry = text("""INSERT INTO Developers
                (userID, developerID, name, mixedOn, capacity, type, kind,
                state, notes)
                VALUES (:userID, :developerID, :name, :mixedOn,
                :capacity, :type, :kind, :state, :notes)""")
            functions.insert(connection, qry, "Developers",
                             userID=userID,
                             developerID=functions.next_id(connection,
                                                           'developerID',
                                                           'Developers'),
                             name=developer_form.name.data,
                             mixedOn=developer_form.mixedOn.data,
                             capacity=developer_form.capacity.data,
                             type=developer_form.type.data,
                             kind=developer_form.kind.data,
                             state=developer_form.state.data,
                             notes=developer_form.notes.data)

    qry = text("""SELECT developerID, name, type, kind FROM Developers
        WHERE userID = :userID
        AND state = 'Active'""")
    active_developers = connection.execute(qry, userID=userID).fetchall()

    qry = text("""SELECT developerID, name, type, kind FROM Developers
        WHERE userID = :userID
        AND state = 'Retired'""")
    retired_developers = connection.execute(qry, userID=userID).fetchall()

    transaction.commit()
    return render_template('/developing/index.html',
                           active_developers=active_developers,
                           retired_developers=retired_developers,
                           developer_form=developer_form)

@app.route('/developing/developer/<int:developerID>', methods=['GET', 'POST'])
@login_required
# pylint: disable=too-many-locals
# Could be refactored to avoid all the lint checks, but no.
def user_developer(developerID):
    """ Developer details """
    connection = engine.connect()
    transaction = connection.begin()
    userID = current_user.get_id()
    developer_form = DeveloperForm()
    developer_log_form = DeveloperLogForm()

    if request.method == 'POST':
        if request.form['button'] == 'retireDeveloper':
            qry = text("""UPDATE Developers
                SET state='Retired'
                WHERE userID = :userID
                AND developerID = :developerID""")
            connection.execute(qry,
                               userID=userID,
                               developerID=developerID)
        if request.form['button'] == 'unretireDeveloper':
            qry = text("""UPDATE Developers
                SET state='Active'
                WHERE userID = :userID
                AND developerID = :developerID""")
            connection.execute(qry,
                               userID=userID,
                               developerID=developerID)
        if request.form['button'] == 'updateDeveloper':
            if developer_form.validate_on_submit():
                qry = text("""UPDATE Developers
                    SET name = :name,
                        mixedOn = :mixedOn,
                        type = :type,
                        kind = :kind,
                        capacity = :capacity,
                        state = :state,
                        notes = :notes
                    WHERE userID = :userID
                    AND developerID = :developerID""")
                connection.execute(qry,
                                   name=developer_form.name.data,
                                   mixedOn=developer_form.mixedOn.data,
                                   type=developer_form.type.data,
                                   kind=developer_form.kind.data,
                                   capacity=developer_form.capacity.data,
                                   state=developer_form.state.data,
                                   notes=developer_form.notes.data,
                                   userID=userID,
                                   developerID=developerID)

        if request.form['button'] == 'addLog':
            if developer_log_form.validate_on_submit():
                try:
                    devTime = functions.time_to_seconds(developer_log_form.devTime.data)
                except ValidationError as e:
                    app.logger.info("Bad dev time format: %s" % e)
                    devTime = None
                qry = text("""INSERT INTO DeveloperLogs
                    (userID, developerID, developerLogID, loggedOn, mlReplaced, mlUsed,
                        temperature, devTime, notes)
                    VALUES (:userID, :developerID, :developerLogID, :loggedOn, :mlReplaced,
                        :mlUsed, :temperature, :devTime, :notes)""")
                connection.execute(qry,
                                   userID=userID,
                                   developerID=developerID,
                                   developerLogID=functions.next_id(connection,
                                                                    'developerLogID',
                                                                    'DeveloperLogs'),
                                   loggedOn=developer_log_form.loggedOn.data,
                                   mlReplaced=developer_log_form.mlReplaced.data,
                                   mlUsed=developer_log_form.mlUsed.data,
                                   temperature=developer_log_form.temperature.data,
                                   devTime=devTime,
                                   notes=developer_log_form.notes.data)

    # Grab the main info for the developer
    qry = text("""SELECT developerID, name, mixedOn, capacity, type, kind,
        state, notes, DATEDIFF(NOW(), mixedOn) AS age
        FROM Developers
        WHERE userID = :userID
        AND developerID = :developerID""")
    developer_results = connection.execute(qry,
                                           userID=userID,
                                           developerID=developerID).fetchone()
    developer = dict(developer_results)

    # If it's a replenished developer, figure out how long it's been since
    # last replenishment
    if developer['kind'] == 'Replenishment':
        qry = text("""SELECT DATEDIFF(NOW(), loggedOn) AS last_replenished
            FROM DeveloperLogs
            WHERE userID = :userID
            AND developerID = :developerID
            AND mlReplaced != 0
            ORDER BY developerLogID DESC LIMIT 1""")
        last_replenished = connection.execute(qry,
                                              userID=userID,
                                              developerID=developerID).fetchone()
        if not last_replenished:
            qry = text("""SELECT DATEDIFF(NOW(), mixedOn) AS last_replenished
                FROM Developers
                WHERE userID = :userID
                AND developerID = :developerID""")
            last_replenished = connection.execute(qry,
                                                  userID=userID,
                                                  developerID=developerID).fetchone()
        last_replenished_dict = dict(last_replenished)
        developer['last_replenished'] = last_replenished_dict['last_replenished']

    # Grab the logs
    qry = text("""SELECT developerLogID, loggedOn, mlReplaced, mlUsed,
        temperature, SECONDS_TO_DURATION(devTime) AS devTime, notes
        FROM DeveloperLogs
        WHERE userID = :userID
        AND developerID = :developerID
        ORDER BY loggedOn DESC""")
    developer_log_results = connection.execute(qry,
                                               userID=userID,
                                               developerID=developerID).fetchall()
    # pylint complains but this took a while to get working so leaving as is.
    # pylint: disable=unnecessary-comprehension
    developer_logs = [{key: value for (key, value) in row.items()}
                      for row in developer_log_results]

    # For each log entry we grab the films used and stuff them into the
    # data dictionary for teh logs. I feel like there is a cleaner way
    # but this works.
    qry = text("""SELECT developerLogFilmID, size AS filmSize,
        DeveloperLogFilms.filmTypeID, FilmTypes.name AS filmName, iso,
        qty, IF(compensation > 0, CONCAT('+', compensation), compensation)
        FROM DeveloperLogFilms
        LEFT OUTER JOIN FilmTypes On FilmTypes.filmTypeID = DeveloperLogFilms.filmTypeID
            AND FilmTypes.userID = DeveloperLogFilms.userID
        JOIN FilmSizes ON FilmSizes.filmSizeID = DeveloperLogFilms.filmSizeID
        WHERE DeveloperLogFilms.userID = :userID
        AND developerLogID = :developerLogID""")

    for index, log in enumerate(developer_logs):
        films = connection.execute(qry,
                                   userID=userID,
                                   developerLogID=log['developerLogID']).fetchall()
        developer_logs[index]['films'] = films

    # Grab film statistics
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
        ORDER BY filmName""")
    film_stats = connection.execute(qry,
                                    userID=userID,
                                    developerID=developerID).fetchall()
    transaction.commit()

    if not developer_form.errors:
        developer_form = DeveloperForm(data=developer)

    return render_template('/developing/developer.html',
                           developer=developer,
                           developer_logs=developer_logs,
                           film_stats=film_stats,
                           developer_form=developer_form,
                           developer_log_form=developer_log_form)

@app.route('/developing/developer/<int:developerID>/log/<int:developerLogID>',
           methods=['GET', 'POST'])
@login_required
def user_developer_log(developerID, developerLogID):
    """ Developer Log Details """
    connection = engine.connect()
    transaction = connection.begin()
    userID = current_user.get_id()
    developer_log_form = DeveloperLogForm()
    developer_log_film_form = DeveloperLogFilmForm()
    developer_log_film_form.populate_select_fields(connection)

    if request.method == 'POST':
        if request.form['button'] == 'updateLog':
            try:
                devTime = functions.time_to_seconds(developer_log_form.devTime.data)
            except ValidationError as e:
                app.logger.info("Bad dev time format: %s" % e)
                devTime = None

            qry = text("""UPDATE DeveloperLogs
                SET loggedOn = :loggedOn, mlReplaced = :mlReplaced,
                    mlUsed = :mlUsed, temperature = :temperature,
                    devTime = :devTime, notes = :notes
                WHERE userID = :userID
                AND developerLogID = :developerLogID""")
            connection.execute(qry,
                               userID=userID,
                               developerLogID=developerLogID,
                               loggedOn=developer_log_form.loggedOn.data,
                               mlReplaced=developer_log_form.mlReplaced.data,
                               mlUsed=developer_log_form.mlUsed.data,
                               temperature=developer_log_form.temperature.data,
                               devTime=devTime,
                               notes=developer_log_form.notes.data)
        if request.form['button'] == 'deleteLog':
            qry = text("""DELETE FROM DeveloperLogs
                WHERE userID = :userID
                AND developerLogID = :developerLogID""")
            connection.execute(qry,
                               userID=userID,
                               developerLogID=developerLogID)
            transaction.commit()
            return redirect('/developing/developer/' + str(developerID))

        if request.form['button'] == 'addFilm':
            if developer_log_film_form.validate_on_submit():
                qry = text("""REPLACE INTO DeveloperLogFilms
                    (userID, developerLogFilmID, developerLogID, filmSizeID,
                        filmTypeID, qty, compensation)
                    VALUES (:userID, :developerLogFilmID, :developerLogID,
                        :filmSizeID, :filmTypeID, :qty, :compensation)""")
                # pylint: disable=line-too-long
                # Haven't found a great way to format this without it being
                # more ugly.
                connection.execute(qry,
                                   userID=userID,
                                   developerLogFilmID=functions.next_id(connection, 'developerLogFilmID', 'DeveloperLogFilms'),
                                   developerLogID=developerLogID,
                                   filmSizeID=developer_log_film_form.filmSizeID.data,
                                   filmTypeID=developer_log_film_form.filmTypeID.data,
                                   qty=developer_log_film_form.qty.data,
                                   compensation=developer_log_film_form.compensation.data)

        if request.form['button'] == 'deleteFilm':
            qry = text("""DELETE FROM DeveloperLogFilms
                WHERE userID = :userID
                AND developerLogFilmID = :developerLogFilmID""")
            connection.execute(qry,
                               userID=userID,
                               developerLogFilmID=int(request.form['developerLogFilmID']))

    # Grab the log
    qry = text("""SELECT developerLogID, loggedOn, mlReplaced, mlUsed,
        temperature, SECONDS_TO_DURATION(devTime) AS devTime, notes
        FROM DeveloperLogs
        WHERE userID = :userID
        AND developerLogID = :developerLogID
        ORDER BY loggedOn DESC""")
    developer_log_results = connection.execute(qry,
                                               userID=userID,
                                               developerID=developerID,
                                               developerLogID=developerLogID).fetchone()
    developer_log = dict(developer_log_results)

    # For each log entry we grab the films used and stuff them into the
    # data dictionary for teh logs. I feel like there is a cleaner way
    # but this works.
    qry = text("""SELECT developerLogFilmID, size AS filmSize,
        DeveloperLogFilms.filmTypeID, FilmTypes.name AS filmName, iso,
        qty, IF(compensation > 0, CONCAT('+', compensation), compensation) AS compensation
        FROM DeveloperLogFilms
        LEFT OUTER JOIN FilmTypes On FilmTypes.filmTypeID = DeveloperLogFilms.filmTypeID
        JOIN FilmSizes ON FilmSizes.filmSizeID = DeveloperLogFilms.filmSizeID
        WHERE DeveloperLogFilms.userID = :userID
        AND developerLogID = :developerLogID""")
    films = connection.execute(qry,
                               userID=userID,
                               developerLogID=developerLogID).fetchall()
    transaction.commit()

    developer_log['films'] = films
    developer_log_form = DeveloperLogForm(data=developer_log)

    return render_template('/developing/developer_log.html',
                           developerID=developerID,
                           developerLogID=developerLogID,
                           developer_log=developer_log,
                           developer_log_form=developer_log_form,
                           developer_log_film_form=developer_log_film_form)
