from flask import request, render_template, redirect, url_for, Response, \
    session, abort, flash, send_from_directory

from sqlalchemy.sql import select, text, func
import os, re

from flask_login import LoginManager, login_required, current_user, login_user, UserMixin

# Forms
from flask_wtf import FlaskForm
from wtforms import Form, StringField, DateField, SelectField, IntegerField, \
    TextAreaField, DecimalField, SelectMultipleField, BooleanField
from wtforms.validators import DataRequired, Optional, Length, NumberRange
from wtforms import widgets

from filmlog import app, csrf, database
from filmlog.functions import next_id, result_to_dict, get_film_details, \
    optional_choices, zero_to_none, get_film_types, get_film_sizes, \
    insert, delete
from filmlog.classes import MultiCheckboxField
from filmlog import users, filmstock, darkroom, files, stats, gear, help, engine, search

## Blueprints
from filmlog.api import api_blueprint
app.register_blueprint(api_blueprint, url_prefix='/api/v1', engine=engine)
csrf.exempt(api_blueprint)

## Functions
def encode_shutter(shutter):
    if re.search(r'^1\/', shutter):
        return re.sub(r'^1\/', r'', shutter)
    elif re.search(r'"', shutter):
        return int(re.sub(r'"', r'', shutter)) * -1
    elif shutter == 'B' or shutter == 'Bulb':
        return 0
    elif shutter != '':
        return shutter

@app.template_filter('format_shutter')
def format_shutter(shutter):
    if shutter > 0:
        return "1/" + str(shutter)
    elif shutter == 0:
        return "B"
    elif shutter:
        return str(abs(shutter)) + "\""

def get_cameras(connection):
    userID = current_user.get_id()
    qry = text("""SELECT cameraID, name
        FROM Cameras
        WHERE userID = :userID""")
    return connection.execute(qry,
        userID = userID).fetchall()

def get_lenses(connection, cameraID):
    userID = current_user.get_id()
    qry = text("""SELECT CameraLenses.lensID AS lensID, name
        FROM CameraLenses
        JOIN Lenses ON Lenses.lensID = CameraLenses.lensID
        WHERE CameraLenses.cameraID = :cameraID
        AND CameraLenses.userID = :userID""")
    return connection.execute(qry,
        userID = userID,
        cameraID = cameraID).fetchall()

def get_filters(connection):
    userID = current_user.get_id()
    qry = text("""SELECT filterID, name
        FROM Filters
        WHERE userID = :userID""")
    return connection.execute(qry,
        userID = userID).fetchall()

# Blindly Decrement Film Stock. If the film does not exist, the UPDATE
# won't do anything. This is currently by design since if a user isn't
# tracking a particular film, no sense in cluttering up the Film Stock.
# We only want to decrement films that are being tracked.
def auto_decrement_film_stock(connection, filmTypeID, filmSizeID):
    userID = current_user.get_id()
    qry = text("""SELECT 1 FROM UserPreferences
        WHERE userID = :userID
        AND autoUpdateFilmStock = 'Yes'""")
    result = connection.execute(qry,
        userID = userID).fetchone()
    if result:
        app.logger.debug("Decrementing Film Stock")
        qry = text("""UPDATE FilmStock SET qty = qty - 1
            WHERE userID = :userID
            AND filmTypeID = :filmTypeID
            AND filmSizeID = :filmSizeID""")
        connection.execute(qry,
            userID = userID,
            filmTypeID = filmTypeID,
            filmSizeID = filmSizeID)

## Form Objects
class BinderForm(FlaskForm):
    name = StringField('Name',
        validators=[DataRequired(), Length(min=1, max=64)])

class ProjectForm(FlaskForm):
    name = StringField('Name',
        validators=[DataRequired(), Length(min=1, max=64)])

class FilmForm(FlaskForm):
    title = StringField('Title',
        validators=[DataRequired(), Length(min=1, max=64)])
    fileNo = StringField('File No.',
        validators=[DataRequired(), Length(min=1, max=32)])

    filmTypeID = SelectField('Film',
        validators=[Optional()],
        coerce=int)
    filmSizeID = SelectField('Film Size',
        validators=[DataRequired()],
        coerce=int)
    cameraID = SelectField('Camera',
        validators=[DataRequired()],
        coerce=int)

    fileDate = DateField('File Date',
        validators=[Optional()])
    loaded = DateField('Loaded',
        validators=[Optional()])
    unloaded = DateField('Unloaded',
        validators=[Optional()])
    developed = DateField('Developed',
        validators=[Optional()])

    shotISO = IntegerField('Shot ISO',
        validators=[NumberRange(min=0,max=65535),
                    Optional()])

    development = StringField('Development',
        validators=[Optional(), Length(min=1, max=255)],
        filters = [lambda x: x or None])
    notes = TextAreaField('Notes',
        validators=[Optional()],
        filters = [lambda x: x or None])

    def populate_select_fields(self, connection):
        self.connection = connection
        self.filmTypeID.choices = optional_choices("None", get_film_types(connection))
        self.filmSizeID.choices = get_film_sizes(connection)
        self.cameraID.choices = get_cameras(connection)

class ExposureForm(FlaskForm):
    exposureNumber = StringField('Exposure #',
        validators=[DataRequired()])
    shutter = StringField('Shutter',
        validators=[Optional(), Length(min=1, max=64)])
    aperture = DecimalField('Aperture', places=1,
        validators=[Optional()],
        filters = [lambda x: x or None])
    lensID = SelectField('Lens',
        validators=[Optional()],
        coerce=int)
    flash = SelectField('Flash',
        validators=[Optional()],
        choices=[('No', 'No'),('Yes', 'Yes')])
    metering = SelectField('Metering',
        validators=[Optional()],
        choices=[(0, 'None'),('Incident', 'Incident'), ('Reflective', 'Reflective')])
    filters = MultiCheckboxField('Filters',
        validators=[Optional()])

    notes = TextAreaField('Notes',
        validators=[Optional()],
        filters = [lambda x: x or None])

    # Extra info for sheets
    subject = StringField('Subject',
        validators=[Optional(), Length(max=255)],
        filters = [lambda x: x or None])
    development = StringField('Development',
        validators=[Optional(), Length(max=255)],
        filters = [lambda x: x or None])
    filmTypeID = SelectField('Film',
        validators=[Optional()],
        coerce=int)
    filmSizeID = SelectField('Film Size',
        validators=[Optional()],
        coerce=int)
    shotISO = IntegerField('Shot ISO',
        validators=[NumberRange(min=0,max=65535),
                    Optional()])

    def populate_select_fields(self, connection, cameraID):
        self.connection = connection
        self.filmTypeID.choices = optional_choices("None", get_film_types(connection))
        self.filmSizeID.choices = optional_choices("None", get_film_sizes(connection))
        self.lensID.choices = optional_choices("None", get_lenses(connection, cameraID))
        self.filters.choices = get_filters(connection)

    def set_exposure_number(self, number):
        self.exposureNumber.data = number

    # This was tough. From a ResultSet we create a list of the id's we
    # want selected, then update the form
    def populate_filter_selections(self, filters):
        selected_filters = []
        for filter in filters:
            selected_filters.append(filter.filterID)
        self.filters.process_data(selected_filters)

@app.route('/',  methods = ['GET'])
def index():
    userID = current_user.get_id()
    if userID:
        return render_template('overview.html')
    else:
        return render_template('public/index.html')

# Binder List
@app.route('/binders',  methods = ['POST', 'GET'])
@login_required
def binders():
    connection = engine.connect()
    transaction = connection.begin()
    userID = current_user.get_id()
    form = BinderForm()

    if request.method == 'POST':
        if form.validate_on_submit():
            nextBinderID = next_id(connection, 'binderID', 'Binders')
            qry = text("""INSERT INTO Binders
                (binderID, userID, name) VALUES (:binderID, :userID, :name)""")
            insert(connection, qry,
                "Binder",
                binderID = nextBinderID,
                userID = userID,
                name = form.name.data)
    qry = text("""SELECT binderID, name, projectCount, createdOn
        FROM Binders WHERE userID = :userID""")
    binders = connection.execute(qry, userID = userID).fetchall()
    transaction.commit()
    return render_template('binders.html', form=form, binders=binders)

# Project List
@app.route('/binders/<int:binderID>/projects',  methods = ['POST', 'GET'])
@login_required
def projects(binderID):
    connection = engine.connect()
    transaction = connection.begin()
    userID = current_user.get_id()
    form = ProjectForm()

    if request.method == 'POST':
        if form.validate_on_submit():
            nextProjectID = next_id(connection, 'projectID', 'Projects')
            qry = text("""INSERT INTO Projects
                (projectID, binderID, userID, name)
                VALUES (:projectID, :binderID, :userID, :name)""")
            insert(connection, qry, "Project",
                projectID = nextProjectID,
                binderID = binderID,
                userID = userID,
                name = form.name.data)

    qry = text("""SELECT binderID, name, projectCount, createdOn
        FROM Binders WHERE userID = :userID
        AND binderID = :binderID""")
    binder = connection.execute(qry,
        binderID = binderID,
        userID = userID).fetchone()

    qry = text("""SELECT projectID, name, filmCount, createdOn FROM Projects
        WHERE binderID = :binderID
        AND userID = :userID
        ORDER BY createdOn""")
    projects = connection.execute(qry, binderID=binderID, userID = userID).fetchall()
    transaction.commit()
    return render_template('projects.html', form=form, binder=binder, binderID=binderID, projects=projects)

# Project Films List
@app.route('/binders/<int:binderID>/projects/<int:projectID>',  methods = ['POST', 'GET'])
@login_required
def project(binderID, projectID):
    connection = engine.connect()
    transaction = connection.begin()
    userID = current_user.get_id()
    form = FilmForm()
    form.populate_select_fields(connection)

    qry = text("""SELECT projectID, Projects.name AS name
        FROM Projects
        JOIN Binders ON Binders.binderID = Projects.binderID
            AND Binders.userID = Projects.userID
        WHERE projectID = :projectID
        AND Projects.binderID = :binderID
        AND Projects.userID = :userID""")
    project = connection.execute(qry,
        projectID = projectID,
        binderID = binderID,
        userID = userID).fetchone()
    if project is None:
        abort(404)

    if request.method == 'POST':
        if form.validate_on_submit():
            filmTypeID = zero_to_none(form.filmTypeID.data)
            filmSizeID = form.filmSizeID.data

            nextFilmID = next_id(connection, 'filmID', 'Films')
            qry = text("""INSERT INTO Films
                (userID, filmID, projectID, cameraID, title, fileNo, fileDate,
                filmTypeID, filmSizeID, iso, loaded, unloaded, developed,
                development, notes)
                VALUES (:userID, :filmID, :projectID, :cameraID, :title,
                        UPPER(:fileNo), :fileDate, :filmTypeID, :filmSizeID,
                        :iso, :loaded, :unloaded,
                        :developed, :development, :notes)""")
            insert(connection, qry, "Film",
                userID = userID,
                filmID = nextFilmID,
                projectID = projectID,
                cameraID = form.cameraID.data,
                title = form.title.data,
                fileNo = form.fileNo.data,
                fileDate = form.fileDate.data,
                filmTypeID = filmTypeID,
                filmSizeID = filmSizeID,
                iso = zero_to_none(form.shotISO.data),
                loaded = form.loaded.data,
                unloaded = form.unloaded.data,
                developed = form.developed.data,
                development = form.development.data,
                notes = form.notes.data)

            # Decrement the logged film from the film stock if the film
            # type was provided and it is a roll film.
            # If it's sheet film, we decrement only when need sheets
            # are added.
            qry = text("""SELECT 1 FROM FilmSizes
                WHERE filmSizeID = :filmSizeID
                AND format = 'Roll'""")
            format = connection.execute(qry, filmSizeID = form.filmSizeID.data).fetchone()
            if format and filmTypeID:
                auto_decrement_film_stock(connection, filmTypeID, filmSizeID)

    qry = text("""SELECT filmID, title, fileNo, fileDate,
        Films.iso AS iso, brand, FilmTypes.name AS filmName,
        FilmSizes.size AS size, exposures,
        Cameras.name AS camera
        FROM Films
        LEFT OUTER JOIN FilmTypes ON FilmTypes.filmTypeID = Films.filmTypeID
        LEFT OUTER JOIN FilmBrands ON FilmBrands.filmBrandID = FilmTypes.filmBrandID
        JOIN FilmSizes ON FilmSizes.filmSizeID = Films.filmSizeID
        JOIN Cameras ON Cameras.cameraID = Films.cameraID
        WHERE projectID = :projectID AND Films.userID = :userID ORDER BY fileDate""")
    films = connection.execute(qry, projectID=projectID, userID=userID).fetchall()
    transaction.commit()

    return render_template('project.html',
        form = form,
        binderID = binderID,
        projectID = projectID,
        project = project,
        films = films)

# Film Exposures
@app.route('/binders/<int:binderID>/projects/<int:projectID>/films/<int:filmID>',  methods = ['POST', 'GET'])
@login_required
def film(binderID, projectID, filmID):
    connection = engine.connect()
    transaction = connection.begin()
    userID = current_user.get_id()

    if request.method == 'POST':
        if request.form['button'] == 'deleteExposure':
            qry = text("""DELETE FROM Exposures
                WHERE filmID = :filmID
                AND exposureNumber = :exposureNumber
                AND userID = :userID""")
            result = connection.execute(qry,
                filmID = filmID,
                userID = userID,
                exposureNumber = int(request.form['exposureNumber']))

        if request.form['button'] == 'editExposure':
            return redirect('/binders/' + str(binderID)
                + '/projects/' + str(projectID)
                + '/films/' + str(filmID)
                + '/exposure/' + request.form['exposureNumber'])

        if request.form['button'] == 'editFilm':
            form = FilmForm()
            form.populate_select_fields(connection)
            if form.validate_on_submit():
                qry = text("""UPDATE Films
                    SET title = :title,
                        fileNo = :fileNo,
                        fileDate = :fileDate,
                        filmTypeID = :filmTypeID,
                        filmSizeID = :filmSizeID,
                        cameraID = :cameraID,
                        iso = :iso,
                        loaded = :loaded,
                        unloaded = :unloaded,
                        developed = :developed,
                        development = :development,
                        notes = :notes
                    WHERE projectID = :projectID
                    AND filmID = :filmID
                    AND userID = :userID""")
                result = connection.execute(qry,
                    userID = userID,
                    filmID = filmID,
                    projectID = projectID,
                    cameraID = form.cameraID.data,
                    title = form.title.data,
                    fileNo = form.fileNo.data,
                    fileDate = form.fileDate.data,
                    filmTypeID = zero_to_none(form.filmTypeID.data),
                    filmSizeID = form.filmSizeID.data,
                    iso = zero_to_none(form.shotISO.data),
                    loaded = form.loaded.data,
                    unloaded = form.unloaded.data,
                    developed = form.developed.data,
                    development = form.development.data,
                    notes = form.notes.data)
                transaction.commit()
                return redirect('/binders/' + str(binderID)
                    + '/projects/' + str(projectID)
                    + '/films/' + str(filmID))
            else:
                film = get_film_details(connection, binderID, projectID, filmID)
                print "HERE"
                app.logger.debug("FilmTypeID: %s", film.filmTypeID)
                return render_template('film/edit-film.html',
                    form=form,
                    binderID=binderID,
                    film=film)

    film = get_film_details(connection, binderID, projectID, filmID)
    if film is None:
        abort(404)


    qry = text("""SELECT cameraID, format
        FROM Films
        LEFT OUTER JOIN FilmSizes ON FilmSizes.filmSizeID = Films.filmSizeID
        WHERE userID = :userID
        AND filmID = :filmID""")
    extras_result = connection.execute(qry,
        userID = userID,
        filmID = filmID).fetchone()
    cameraID = extras_result[0]
    filmFormat = extras_result[1]

    qry = text("""SELECT exposureNumber, shutter, aperture,
        Lenses.name AS lens, flash, metering, subject, notes, development,
        Exposures.iso AS shotISO,
        FilmTypes.name AS filmType, FilmTypes.iso AS filmISO,
        FilmBrands.brand AS filmBrand
        FROM Exposures
        LEFT JOIN Lenses ON Lenses.lensID = Exposures.lensID
        LEFT OUTER JOIN FilmTypes ON FilmTypes.filmTypeID = Exposures.filmTypeID
        LEFT OUTER JOIN FilmBrands ON FilmBrands.filmBrandID = FilmTypes.filmBrandID
        WHERE filmID = :filmID
        AND Exposures.userID = :userID
        ORDER BY exposureNumber""")
    exposuresResult = connection.execute(qry, filmID=filmID, userID=userID).fetchall()
    exposures = result_to_dict(exposuresResult)
    for exposure in exposures:
        qry = text("""SELECT code FROM ExposureFilters
            JOIN Filters ON Filters.filterID = ExposureFilters.filterID
            WHERE filmID = :filmID
            AND exposureNumber = :exposureNumber
            AND ExposureFilters.userID = :userID""")
        filtersResult = connection.execute(qry, filmID=filmID,
            userID = userID,
            exposureNumber = exposure['exposureNumber']).fetchall()
        exposureFilters = result_to_dict(filtersResult)
        exposure['filters'] = exposureFilters

    qry = text("""SELECT MAX(exposureNumber) AS max FROM Exposures
        WHERE filmID = :filmID AND userID = :userID""")
    lastExposureResult = connection.execute(qry, filmID=filmID, userID=userID).first()
    if not lastExposureResult[0]:
        last_exposure = 0
    else:
        last_exposure = lastExposureResult[0]

    if request.args.get('print'):
        print_view = True
        if film.filmSizeType == 'Small':
            template = 'film/35mm-print.html'
        if film.filmSizeType == 'Medium':
            template = 'film/120-print.html'
        if film.size == '4x5':
            template = 'film/lf-print.html'
        if film.size == '8x10':
            template = 'film/lf-print.html'
    elif request.args.get('edit'):
        film = get_film_details(connection, binderID, projectID, filmID)
        form = FilmForm(data=film)
        form.populate_select_fields(connection)
        transaction.commit()
        return render_template('film/edit-film.html',
            form=form,
            binderID=binderID,
            film=film)
    else:
        print_view = False
        app.logger.debug("filmSizeType: %s", film.filmSizeType)
        if film.filmSizeType == 'Small':
            template = 'film/35mm.html'
        if film.filmSizeType == 'Medium':
            template = 'film/120.html'
        if film.size == '4x5':
            template = 'film/lf.html';
        if film.size == '8x10':
            template = 'film/lf.html';

    form = ExposureForm()
    form.populate_select_fields(connection, film.cameraID)
    exposureNumber = last_exposure + 1
    form.set_exposure_number(exposureNumber)
    transaction.commit()
    return render_template(template,
        form=form,
        binderID=binderID, projectID=projectID, filmID=filmID,
        film=film, exposures=exposures, exposureNumber=exposureNumber,
        filmFormat = filmFormat,
        print_view=print_view,
        view='exposures')

# Edit Exposure
@app.route('/binders/<int:binderID>/projects/<int:projectID>/films/<int:filmID>/exposure/<int:exposureNumber>',  methods = ['POST', 'GET'])
@login_required
def expsoure(binderID, projectID, filmID, exposureNumber):
    connection = engine.connect()
    transaction = connection.begin()
    userID = current_user.get_id()

    if request.method == 'POST':
        form = ExposureForm()
        filmSizeID = zero_to_none(form.filmSizeID.data)

        if request.form['button'] == 'addExposure':
            # If exposure number has a dash, it means
            # we are adding a range of exposures
            exposureNumber = form.exposureNumber.data
            if re.search("-", exposureNumber):
                ranges = exposureNumber.split("-", 2)
                sequence = range(int(ranges[0]), int(ranges[1]))
            else:
                sequence = [int(exposureNumber)]
            for exposure in sequence:
                qry = text("""INSERT INTO Exposures
                    (userID, filmID, exposureNumber, lensID, shutter, aperture, filmTypeID, iso, metering, flash, subject, development, notes)
                    VALUES (:userID, :filmID, :exposureNumber, :lensID, :shutter, :aperture, :filmTypeID, :shotISO, :metering, :flash, :subject, :development, :notes)""")
                insert(connection, qry, "Exposure",
                    userID = userID,
                    filmID = filmID,
                    exposureNumber = exposure,
                    lensID = zero_to_none(form.lensID.data),
                    shutter = encode_shutter(form.shutter.data),
                    aperture = form.aperture.data,
                    filmTypeID = zero_to_none(form.filmTypeID.data),
                    shotISO = zero_to_none(form.shotISO.data),
                    metering = zero_to_none(form.metering.data),
                    flash = form.flash.data,
                    subject = form.subject.data,
                    development = form.development.data,
                    notes = form.notes.data)

                qry = text("""INSERT INTO ExposureFilters
                (userID, filmID, exposureNumber, filterID)
                VALUES (:userID, :filmID, :exposureNumber, :filterID)""")
                for filterID in form.filters.data:
                    insert(connection, qry, "Filter",
                    userID = userID,
                    filmID = filmID,
                    exposureNumber = exposure,
                    filterID = filterID)

            # Decrement film stock for exposures if relevant

            # First we get basic info about the film log
            qry = text("""SELECT filmTypeID, filmSizeID FROM Films
                WHERE projectID = :projectID
                AND filmID = :filmID
                AND userID = :userID""")
            filmInfo = connection.execute(qry,
                projectID = projectID,
                filmID = filmID,
                userID = userID).fetchone()
            filmTypeID = filmInfo.filmTypeID
            filmSizeID = filmInfo.filmSizeID

            # Decrement the logged film from the film stock if the film
            # type was provided and it is a sheet.
            qry = text("""SELECT 1 FROM FilmSizes
                WHERE filmSizeID = :filmSizeID
                AND format = 'Sheet'""")
            format = connection.execute(qry,
                filmSizeID = filmSizeID).fetchone()
            if format:
                # First look at the film type from the sheet
                if zero_to_none(form.filmTypeID.data):
                    auto_decrement_film_stock(connection, form.filmTypeID.data, filmSizeID)
                # If that doesn't exist, we use the global film type
                else:
                    auto_decrement_film_stock(connection, filmTypeID, filmSizeID)

        if request.form['button'] == 'updateExposure':
            qry = text("""UPDATE Exposures
                SET exposureNumber = :exposureNumberNew,
                    shutter = :shutter,
                    aperture = :aperture,
                    lensID = :lensID,
                    flash = :flash,
                    metering = :metering,
                    notes = :notes,
                    subject = :subject,
                    development = :development,
                    filmTypeID = :filmTypeID,
                    iso = :shotISO
                WHERE filmID = :filmID
                AND exposureNumber = :exposureNumberOld
                AND userID = :userID""")
            connection.execute(qry,
                userID = userID,
                filmID = filmID,
                exposureNumberNew = form.exposureNumber.data,
                exposureNumberOld = exposureNumber,
                lensID = zero_to_none(form.lensID.data),
                shutter = encode_shutter(form.shutter.data),
                aperture = form.aperture.data,
                filmTypeID = zero_to_none(form.filmTypeID.data),
                filmSizeID = filmSizeID,
                shotISO = zero_to_none(form.shotISO.data),
                metering = zero_to_none(form.metering.data),
                flash = form.flash.data,
                subject = form.subject.data,
                development = form.development.data,
                notes = form.notes.data)

            qry = text("""DELETE FROM ExposureFilters
                WHERE filmID = :filmID
                AND exposureNumber = :exposureNumber
                AND userID = :userID""")
            connection.execute(qry, filmID = filmID,
                userID = userID,
                exposureNumber = request.form['exposureNumber'])

            qry = text("""INSERT INTO ExposureFilters
                (userID, filmID, exposureNumber, filterID)
                VALUES (:userID, :filmID, :exposureNumber, :filterID)""")
            for filterID in request.form.getlist('filters'):
                insert(connection, qry, "Filter",
                    userID = userID,
                    filmID = filmID,
                    exposureNumber = request.form['exposureNumber'],
                    filterID = filterID)
        transaction.commit()
        return redirect('/binders/' + str(binderID)
            + '/projects/' + str(projectID)
            + '/films/' + str(filmID))

    qry = text("""SELECT exposureNumber, shutter, aperture,
        lensID, flash, notes, metering, subject, development, filmTypeID, iso
        FROM Exposures
        WHERE filmID = :filmID
        AND exposureNumber = :exposureNumber
        AND userID = :userID""")
    exposure_result = connection.execute(qry,
        filmID=filmID,
        exposureNumber=exposureNumber,
        userID = userID).fetchall()
    row = result_to_dict(exposure_result)
    exposure = row[0]
    exposure['shutter'] = format_shutter(exposure['shutter'])

    qry = text("""SELECT cameraID, format
        FROM Films
        LEFT OUTER JOIN FilmSizes ON FilmSizes.filmSizeID = Films.filmSizeID
        WHERE userID = :userID
        AND filmID = :filmID""")
    extras_result = connection.execute(qry,
        userID = userID,
        filmID = filmID).fetchone()
    cameraID = extras_result[0]
    filmFormat = extras_result[1]

    qry = text("""SELECT Filters.filterID AS filterID FROM ExposureFilters
        JOIN Filters ON Filters.filterID = ExposureFilters.filterID
        WHERE filmID = :filmID
        AND exposureNumber = :exposureNumber
        AND ExposureFilters.userID = :userID""")
    filtersResult = connection.execute(qry, filmID=filmID,
        exposureNumber = exposureNumber,
        userID = userID).fetchall()
    transaction.commit()

    form = ExposureForm()
    form = ExposureForm(data=exposure)
    form.populate_select_fields(connection, cameraID)
    form.populate_filter_selections(filtersResult)

    return render_template('film/edit-exposure.html',
        form=form,
        userID=userID,
        binderID=binderID,
        projectID=projectID,
        filmID=filmID,
        filmFormat=filmFormat,
        exposureNumber=exposureNumber,
        film=film)
