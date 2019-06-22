""" Main body of filmlog web (non API) for handling the app routing.
    Sections (e.g. /gear) will come from other files to break things appart
    in a useful way without having to go deep into blueprints. """
import re
import datetime
from flask import request, render_template, redirect, abort
from flask_login import login_required, current_user
from sqlalchemy.sql import text

# Forms
from flask_wtf import FlaskForm
from wtforms import StringField, DateField, SelectField, IntegerField, \
    TextAreaField, DecimalField
from wtforms.validators import DataRequired, Optional, Length, NumberRange

# Filmlog
from filmlog import config
from filmlog.functions import result_to_dict, get_film_details, \
    optional_choices, zero_to_none, get_film_types, get_film_sizes, \
    insert
from filmlog.classes import MultiCheckboxField

# pylint: disable=unused-import
# Could be a better way to do this, but these are used to section out parts
# of the app into logical groupings (e.g. darkroom is for /darkroom)
# Blueprints may be the answer here.
from filmlog import users, filmstock, darkroom, files, gear, docs, \
    search, developing

## Blueprints
from filmlog.api import api_blueprint

app = config.app
engine = config.engine
csrf = config.csrf

app.register_blueprint(api_blueprint, url_prefix='/api/v1', engine=engine)
csrf.exempt(api_blueprint)

## Functions
def encode_shutter(shutter):
    """ Helper function to encode the shutter into a format suitable
        for the database. """
    if re.search(r'^1\/', shutter):
        return re.sub(r'^1\/', r'', shutter)
    if re.search(r'"', shutter):
        return int(re.sub(r'"', r'', shutter)) * -1
    if shutter in ('B', 'Bulb'):
        return 0
    if shutter != '':
        return shutter
    return None

@app.template_filter('format_shutter')
def format_shutter(shutter):
    """ Helper function to encode the shutter value from the database
        into a human readable format. """
    if not shutter:
        return None
    if shutter > 0:
        return "1/" + str(shutter)
    if shutter == 0:
        return "B"
    if shutter:
        if abs(shutter) > 60:
            return str(datetime.timedelta(seconds=abs(shutter)))
        return str(abs(shutter)) + "\""
    return None

def get_cameras(connection):
    """ Get the user's cameras. """
    userID = current_user.get_id()
    qry = text("""SELECT cameraID, name
        FROM Cameras
        WHERE userID = :userID
        AND status = 'Active'""")
    return connection.execute(qry,
                              userID=userID).fetchall()

def get_lenses(connection, cameraID):
    """ Get the user's lenses for a camera. """
    userID = current_user.get_id()
    qry = text("""SELECT CameraLenses.lensID AS lensID, name
        FROM CameraLenses
        JOIN Lenses ON Lenses.lensID = CameraLenses.lensID
            AND Lenses.userID = CameraLenses.userID
        WHERE CameraLenses.cameraID = :cameraID
        AND CameraLenses.userID = :userID""")
    return connection.execute(qry,
                              userID=userID,
                              cameraID=cameraID).fetchall()

def get_filters(connection):
    """ Get the user's filters. """
    userID = current_user.get_id()
    qry = text("""SELECT filterID, name
        FROM Filters
        WHERE userID = :userID""")
    return connection.execute(qry,
                              userID=userID).fetchall()

def get_holders(connection):
    """ Get the user's large format film holders. """
    userID = current_user.get_id()
    qry = text("""SELECT holderID, name
        FROM Holders
        WHERE userID = :userID""")
    return connection.execute(qry,
                              userID=userID).fetchall()

def auto_decrement_film_stock(connection, filmTypeID, filmSizeID):
    """ Blindly Decrement Film Stock. If the film does not exist, the UPDATE
        won't do anything. This is currently by design since if a user isn't
        tracking a particular film, no sense in cluttering up the Film Stock.
        We only want to decrement films that are being tracked. """
    userID = current_user.get_id()
    qry = text("""SELECT 1 FROM UserPreferences
        WHERE userID = :userID
        AND autoUpdateFilmStock = 'Yes'""")
    result = connection.execute(qry,
                                userID=userID).fetchone()
    if result:
        app.logger.debug("Decrementing Film Stock")
        qry = text("""UPDATE FilmStock SET qty = qty - 1
            WHERE userID = :userID
            AND filmTypeID = :filmTypeID
            AND filmSizeID = :filmSizeID""")
        connection.execute(qry,
                           userID=userID,
                           filmTypeID=filmTypeID,
                           filmSizeID=filmSizeID)

## Form Objects
class FilmForm(FlaskForm):
    """ Form for user films. """
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
    fileDate = DateField('File Date', validators=[Optional()])
    loaded = DateField('Loaded', validators=[Optional()])
    unloaded = DateField('Unloaded', validators=[Optional()])
    developed = DateField('Developed', validators=[Optional()])
    shotISO = IntegerField('Shot ISO',
                           validators=[NumberRange(min=0, max=65535),
                                       Optional()])
    development = StringField('Development',
                              validators=[Optional(), Length(min=1, max=255)],
                              filters=[lambda x: x or None])
    notes = TextAreaField('Notes',
                          validators=[Optional()],
                          filters=[lambda x: x or None])

    def populate_select_fields(self, connection):
        """ Helper function to populate choices for the form. """
        self.filmTypeID.choices = optional_choices("None", get_film_types(connection))
        self.filmSizeID.choices = get_film_sizes(connection)
        self.cameraID.choices = get_cameras(connection)


class ExposureForm(FlaskForm):
    """ For User's Exposures """
    exposureNumber = StringField('Exposure #',
                                 validators=[DataRequired()])
    shutter = StringField('Shutter',
                          validators=[Optional(), Length(min=1, max=64)])
    aperture = DecimalField('Aperture', places=1,
                            validators=[Optional()],
                            filters=[lambda x: x or None])
    lensID = SelectField('Lens',
                         validators=[Optional()],
                         coerce=int)
    flash = SelectField('Flash',
                        validators=[Optional()],
                        choices=[('No', 'No'), ('Yes', 'Yes')])
    metering = SelectField('Metering',
                           validators=[Optional()],
                           choices=[(0, 'None'),
                                    ('Incident', 'Incident'),
                                    ('Reflective', 'Reflective')])
    filters = MultiCheckboxField('Filters',
                                 validators=[Optional()])
    notes = TextAreaField('Notes',
                          validators=[Optional()],
                          filters=[lambda x: x or None])
    # Extra info for sheets
    subject = StringField('Subject',
                          validators=[Optional(), Length(max=255)],
                          filters=[lambda x: x or None])
    development = StringField('Development',
                              validators=[Optional(), Length(max=255)],
                              filters=[lambda x: x or None])
    filmTypeID = SelectField('Film',
                             validators=[Optional()],
                             coerce=int)
    filmSizeID = SelectField('Film Size',
                             validators=[Optional()],
                             coerce=int)
    holderID = SelectField('Film Holder',
                           validators=[Optional()],
                           coerce=int)
    shotISO = IntegerField('Shot ISO',
                           validators=[NumberRange(min=0, max=65535),
                                       Optional()])

    def populate_select_fields(self, connection, cameraID):
        """ Helper function to populate choices for the form. """
        self.filmTypeID.choices = optional_choices("None", get_film_types(connection))
        self.filmSizeID.choices = optional_choices("None", get_film_sizes(connection))
        self.lensID.choices = optional_choices("None", get_lenses(connection, cameraID))
        self.holderID.choices = optional_choices("None", get_holders(connection))
        self.filters.choices = get_filters(connection)

    def set_exposure_number(self, number):
        """ Set the exposure. """
        self.exposureNumber.data = number

    def populate_filter_selections(self, filters):
        """ This was tough. From a ResultSet we create a list of the id's we
            want selected, then update the form. """
        selected_filters = []
        for single_filter in filters:
            selected_filters.append(single_filter.filterID)
        self.filters.process_data(selected_filters)

@app.route('/', methods=['GET'])
def index():
    """ Main index. If the user is logged in we display their home page.
        Otherwise we display the generic public page. """
    connection = engine.connect()
    transaction = connection.begin()
    userID = current_user.get_id()
    if userID:
        qry = text("""SELECT COUNT(*) AS cnt FROM Binders
            WHERE userID = :userID""")
        binder_count = connection.execute(qry, userID=userID).fetchone()


        qry = text("""SELECT Cameras.name, COUNT(Films.cameraID) AS count
            FROM Cameras
            JOIN Films ON Films.cameraID = Cameras.cameraID
            AND Films.userID = Cameras.userID
            WHERE Cameras.userID=:userID
            GROUP BY Films.cameraID
            ORDER BY COUNT(Films.cameraID) DESC""")
        cameras = connection.execute(qry, userID=userID)

        qry = text("""SELECT
            FilmBrands.brand AS brand, FilmTypes.name AS type, FilmTypes.iso AS iso,
            COUNT(Films.filmTypeID) AS count
            FROM Films
            JOIN FilmTypes ON FilmTypes.filmTypeID = Films.filmTypeID
            JOIN FilmBrands ON FilmBrands.filmBrandID = FilmTypes.filmBrandID
            AND userID = :userID
            GROUP BY Films.filmTypeID
            ORDER BY COUNT(Films.filmTypeID) DESC""")
        favoriteRolls = connection.execute(qry, userID=userID)

        qry = text("""SELECT
            FilmBrands.brand AS brand, FilmTypes.name AS type, FilmTypes.iso AS iso,
            COUNT(Exposures.filmTypeID) AS count
            FROM Exposures
            JOIN Films on Films.filmID = Exposures.filmID
                AND Films.userID = Exposures.userID
            JOIN FilmTypes ON FilmTypes.filmTypeID = Exposures.filmTypeID
            JOIN FilmBrands ON FilmBrands.filmBrandID = FilmTypes.filmBrandID
            AND Exposures.userID = :userID
            GROUP BY Exposures.filmTypeID
            ORDER BY COUNT(Exposures.filmTypeID) DESC""")
        favoriteSheets = connection.execute(qry, userID=userID)

        transaction.commit()
        return render_template('/overview.html',
                               binder_count=binder_count.cnt,
                               cameras=cameras,
                               favoriteRolls=favoriteRolls,
                               favoriteSheets=favoriteSheets)

    transaction.rollback()
    return render_template('public/index.html')

@app.route('/contribute', methods=['GET'])
def contribute():
    """ Static page for contributions """
    return render_template('/public/contribute.html')

@app.route('/thankyou', methods=['GET'])
def thankyou():
    """ Thank you page (return page from donations) """
    return render_template('/public/thankyou.html')

# Binder List
@app.route('/binders', methods=['GET'])
@login_required
def user_binders():
    """ List all the user's binders. """
    return render_template('binders.html')

# Project List
@app.route('/binders/<int:binderID>/projects', methods=['GET'])
@login_required
# pylint: disable=unused-argument
# Sort of required for pathing otherwise it throws errors
def user_projects(binderID):
    """ List out the projects from the binder (for the logged in user). """
    return render_template('projects.html')

# Project Films List
@app.route('/binders/<int:binderID>/projects/<int:projectID>', methods=['POST', 'GET'])
@login_required
# pylint: disable=unused-argument
# Sort of required for pathing otherwise it throws errors
def user_project(binderID, projectID):
    """ List out the films within the project for the logged in user """
    return render_template('project.html')

# Film Exposures
@app.route('/binders/<int:binderID>/projects/<int:projectID>/films/<int:filmID>',
           methods=['POST', 'GET'])
@login_required
def user_film(binderID, projectID, filmID):
    """ Provide details about the given user's film, including the exposures.
        For roll film, the exposures are more obvious. For sheet film, they
        are individual sheets group by this film (so it is a bit of a
        sub project of the project). """
    # pylint: disable=too-many-locals,too-many-branches,too-many-statements
    # Could be refactored to avoid all the lint checks, but this is a
    # complicated part of the website in general.

    connection = engine.connect()
    transaction = connection.begin()
    userID = current_user.get_id()

    if request.method == 'POST':
        if request.form['button'] == 'deleteExposure':
            qry = text("""DELETE FROM Exposures
                WHERE filmID = :filmID
                AND exposureNumber = :exposureNumber
                AND userID = :userID""")
            connection.execute(qry,
                               filmID=filmID,
                               userID=userID,
                               exposureNumber=int(request.form['exposureNumber']))

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
                connection.execute(qry,
                                   userID=userID,
                                   filmID=filmID,
                                   projectID=projectID,
                                   cameraID=form.cameraID.data,
                                   title=form.title.data,
                                   fileNo=form.fileNo.data,
                                   fileDate=form.fileDate.data,
                                   filmTypeID=zero_to_none(form.filmTypeID.data),
                                   filmSizeID=form.filmSizeID.data,
                                   iso=zero_to_none(form.shotISO.data),
                                   loaded=form.loaded.data,
                                   unloaded=form.unloaded.data,
                                   developed=form.developed.data,
                                   development=form.development.data,
                                   notes=form.notes.data)
                transaction.commit()
                return redirect('/binders/' + str(binderID)
                                + '/projects/' + str(projectID)
                                + '/films/' + str(filmID))
            # Still in outer if
            film = get_film_details(connection, binderID, projectID, filmID)
            app.logger.debug("FilmTypeID: %s", film.filmTypeID)
            return render_template('film/edit-film.html',
                                   form=form,
                                   binderID=binderID,
                                   film=film)

    film = get_film_details(connection, binderID, projectID, filmID)
    if film is None:
        abort(404)

    qry = text("""SELECT format
        FROM Films
        LEFT OUTER JOIN FilmSizes ON FilmSizes.filmSizeID = Films.filmSizeID
        WHERE userID = :userID
        AND filmID = :filmID""")
    extras_result = connection.execute(qry,
                                       userID=userID,
                                       filmID=filmID).fetchone()
    filmFormat = extras_result[0]

    qry = text("""SELECT exposureNumber, Exposures.shutter AS shutter, aperture,
        Lenses.name AS lens, flash, metering, subject, Exposures.notes, development,
        Exposures.iso AS shotISO,
        FilmTypes.name AS filmType, FilmTypes.iso AS filmISO,
        FilmBrands.brand AS filmBrand,
        Holders.name AS holderName,
        Holders.holderID AS holderID
        FROM Exposures
        LEFT JOIN Lenses ON Lenses.lensID = Exposures.lensID
            AND Lenses.userID = Exposures.userID
        LEFT JOIN Holders ON Holders.holderID = Exposures.holderID
            AND Holders.userID = Exposures.userID
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
                AND Filters.userID = ExposureFilters.userID
            WHERE filmID = :filmID
            AND exposureNumber = :exposureNumber
            AND ExposureFilters.userID = :userID""")
        filtersResult = connection.execute(qry,
                                           filmID=filmID,
                                           userID=userID,
                                           exposureNumber=exposure['exposureNumber']).fetchall()
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
            template = 'film/lf.html'
        if film.size == '8x10':
            template = 'film/lf.html'

    form = ExposureForm()
    form.populate_select_fields(connection, film.cameraID)
    exposureNumber = last_exposure + 1
    form.set_exposure_number(exposureNumber)
    transaction.commit()
    return render_template(template,
                           form=form,
                           binderID=binderID,
                           projectID=projectID,
                           filmID=filmID,
                           film=film,
                           exposures=exposures,
                           exposureNumber=exposureNumber,
                           filmFormat=filmFormat,
                           print_view=print_view,
                           view='exposures')

# Edit Exposure
@app.route('/binders/<int:binderID>/projects/<int:projectID>/films/' +
           '<int:filmID>/exposure/<int:exposureNumber>',
           methods=['POST', 'GET'])
@login_required
def expsoure_details(binderID, projectID, filmID, exposureNumber):
    """ Detailed exposure information """
    # pylint: disable=too-many-locals
    # Another heavierweight part of the app which could stand to be improved,
    # but works for now.

    connection = engine.connect()
    transaction = connection.begin()
    userID = current_user.get_id()

    if request.method == 'POST':
        form = ExposureForm()
        filmSizeID = zero_to_none(form.filmSizeID.data)

        if request.form['button'] == 'addExposure':
            # First we get basic info about the film log
            qry = text("""SELECT filmTypeID, filmSizeID FROM Films
                WHERE projectID = :projectID
                AND filmID = :filmID
                AND userID = :userID""")
            filmInfo = connection.execute(qry,
                                          projectID=projectID,
                                          filmID=filmID,
                                          userID=userID).fetchone()
            filmTypeID = filmInfo.filmTypeID
            filmSizeID = filmInfo.filmSizeID

            # Determine if the format is sheet film
            qry = text("""SELECT 1 FROM FilmSizes
                WHERE filmSizeID = :filmSizeID
                AND format = 'Sheet'""")
            sheet_film = connection.execute(qry,
                                            filmSizeID=filmSizeID).fetchone()

            # If exposure number has a dash, it means
            # we are adding a range of exposures
            exposureNumber = form.exposureNumber.data
            if re.search("-", exposureNumber):
                ranges = exposureNumber.split("-", 2)
                sequence = range(int(ranges[0]), int(ranges[1]) + 1)
            else:
                sequence = [int(exposureNumber)]
            for exposure in sequence:
                qry = text("""INSERT INTO Exposures
                    (userID, filmID, exposureNumber, lensID, holderID, shutter, aperture,
                    filmTypeID, iso, metering, flash, subject, development, notes)
                    VALUES (:userID, :filmID, :exposureNumber, :lensID, :holderID,
                    :shutter, :aperture, :filmTypeID, :shotISO, :metering,
                    :flash, :subject, :development, :notes)""")
                insert(connection, qry, "Exposure",
                       userID=userID,
                       filmID=filmID,
                       exposureNumber=exposure,
                       lensID=zero_to_none(form.lensID.data),
                       holderID=zero_to_none(form.holderID.data),
                       shutter=encode_shutter(form.shutter.data),
                       aperture=form.aperture.data,
                       filmTypeID=zero_to_none(form.filmTypeID.data),
                       shotISO=zero_to_none(form.shotISO.data),
                       metering=zero_to_none(form.metering.data),
                       flash=form.flash.data,
                       subject=form.subject.data,
                       development=form.development.data,
                       notes=form.notes.data)

                qry = text("""INSERT INTO ExposureFilters
                (userID, filmID, exposureNumber, filterID)
                VALUES (:userID, :filmID, :exposureNumber, :filterID)""")
                for filterID in form.filters.data:
                    insert(connection, qry, "Filter",
                           userID=userID,
                           filmID=filmID,
                           exposureNumber=exposure,
                           filterID=filterID)

                if sheet_film:
                    auto_decrement_film_stock(connection,
                                              filmTypeID,
                                              filmSizeID)

        if request.form['button'] == 'updateExposure':
            qry = text("""UPDATE Exposures
                SET exposureNumber = :exposureNumberNew,
                    shutter = :shutter,
                    aperture = :aperture,
                    lensID = :lensID,
                    holderID = :holderID,
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
                               userID=userID,
                               filmID=filmID,
                               exposureNumberNew=form.exposureNumber.data,
                               exposureNumberOld=exposureNumber,
                               lensID=zero_to_none(form.lensID.data),
                               holderID=zero_to_none(form.holderID.data),
                               shutter=encode_shutter(form.shutter.data),
                               aperture=form.aperture.data,
                               filmTypeID=zero_to_none(form.filmTypeID.data),
                               filmSizeID=filmSizeID,
                               shotISO=zero_to_none(form.shotISO.data),
                               metering=zero_to_none(form.metering.data),
                               flash=form.flash.data,
                               subject=form.subject.data,
                               development=form.development.data,
                               notes=form.notes.data)

            qry = text("""DELETE FROM ExposureFilters
                WHERE filmID = :filmID
                AND exposureNumber = :exposureNumber
                AND userID = :userID""")
            connection.execute(qry,
                               filmID=filmID,
                               userID=userID,
                               exposureNumber=request.form['exposureNumber'])

            qry = text("""INSERT INTO ExposureFilters
                (userID, filmID, exposureNumber, filterID)
                VALUES (:userID, :filmID, :exposureNumber, :filterID)""")
            for filterID in request.form.getlist('filters'):
                insert(connection, qry, "Filter",
                       userID=userID,
                       filmID=filmID,
                       exposureNumber=request.form['exposureNumber'],
                       filterID=filterID)
        transaction.commit()
        return redirect('/binders/' + str(binderID)
                        + '/projects/' + str(projectID)
                        + '/films/' + str(filmID))

    qry = text("""SELECT exposureNumber, shutter, aperture,
        lensID, flash, notes, metering, subject, development, filmTypeID,
        iso AS shotISO, holderID
        FROM Exposures
        WHERE filmID = :filmID
        AND exposureNumber = :exposureNumber
        AND userID = :userID""")
    exposure_result = connection.execute(qry,
                                         filmID=filmID,
                                         exposureNumber=exposureNumber,
                                         userID=userID).fetchall()
    row = result_to_dict(exposure_result)
    exposure = row[0]
    exposure['shutter'] = format_shutter(exposure['shutter'])

    qry = text("""SELECT cameraID, format
        FROM Films
        LEFT OUTER JOIN FilmSizes ON FilmSizes.filmSizeID = Films.filmSizeID
        WHERE userID = :userID
        AND filmID = :filmID""")
    extras_result = connection.execute(qry,
                                       userID=userID,
                                       filmID=filmID).fetchone()
    cameraID = extras_result[0]
    filmFormat = extras_result[1]

    qry = text("""SELECT Filters.filterID AS filterID FROM ExposureFilters
        JOIN Filters ON Filters.filterID = ExposureFilters.filterID
        WHERE filmID = :filmID
        AND exposureNumber = :exposureNumber
        AND ExposureFilters.userID = :userID""")
    filtersResult = connection.execute(qry,
                                       filmID=filmID,
                                       exposureNumber=exposureNumber,
                                       userID=userID).fetchall()
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
                           exposureNumber=exposureNumber)
