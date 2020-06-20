""" Gear specific views (/gear) """
from flask import request, render_template, redirect
from flask_login import login_required, current_user
from sqlalchemy.sql import text

# Forms
from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, IntegerField, TextAreaField, \
                    DecimalField
from wtforms.validators import DataRequired, Optional, Length, NumberRange

# Filmlog
from filmlog.config import app, engine
from filmlog.functions import next_id, insert, delete, optional_choices, \
                              get_film_types, zero_to_none
from filmlog.classes import MultiCheckboxField

def get_lenses(connection):
    """ Get the all user's lenses """
    userID = current_user.get_id()
    qry = text("""SELECT lensID, name
        FROM Lenses
        WHERE userID = :userID""")
    return connection.execute(qry, userID=userID).fetchall()

class EnlargerLensForm(FlaskForm):
    """ Form for enlarger lenses """
    name = StringField('Name', validators=[DataRequired(),
                                           Length(min=1, max=64)])

class EnlargerForm(FlaskForm):
    """ Form for enlargers """
    name = StringField('Name',
                       validators=[DataRequired(), Length(min=1, max=64)])
    type = SelectField('Type',
                       validators=[DataRequired()],
                       choices=[('Condenser', 'Condenser'),
                                ('Diffuser', 'Diffuser')])
    lightsource = SelectField('Type',
                              validators=[DataRequired()],
                              choices=[('LED', 'LED'),
                                       ('Incandescent', 'Incandescent'),
                                       ('Cold Light', 'Cold Light')])
    wattage = IntegerField('Wattage',
                           validators=[NumberRange(min=0, max=65535),
                                       Optional()])
    temperature = IntegerField('Temperature (K)',
                               validators=[NumberRange(min=0, max=65535),
                                           Optional()])
    notes = TextAreaField('Notes',
                          validators=[Optional()],
                          filters=[lambda x: x or None])

class CameraForm(FlaskForm):
    """ Form for updating a user's camera """
    name = StringField('Name',
                       validators=[DataRequired(), Length(min=1, max=64)])
    filmSize = SelectField('Film Size',
                           validators=[DataRequired()],
                           choices=[('35mm', '35mm'),
                                    ('120', '120'),
                                    ('220', '220'),
                                    ('4x5', '4x5'),
                                    ('8x10', '8x10')])
    status = SelectField('Status',
                         validators=[DataRequired()],
                         choices=[('Active', 'Active'),
                                  ('Inactive', 'Inactive')])
    lenses = MultiCheckboxField('Lenses',
                                validators=[Optional()])

    def populate_select_fields(self, connection):
        """ Helper function to populate select fields """
        self.lenses.choices = get_lenses(connection)

    def populate_lens_selections(self, lenses):
        """ Helper function to checkbox lenses associated with camera """
        selected_lenses = []
        for this_lens in lenses:
            selected_lenses.append(this_lens.lensID)
        self.lenses.process_data(selected_lenses)

class FilterForm(FlaskForm):
    """ Form for updating user's lens filters """
    name = StringField('Name',
                       validators=[DataRequired(), Length(min=1, max=64)])
    code = StringField('Code',
                       validators=[DataRequired(), Length(min=1, max=8)])
    factor = DecimalField('Factor', places=1, validators=[DataRequired()])
    ev = DecimalField('EV', places=1, validators=[DataRequired()])

class CameraLensForm(FlaskForm):
    """ Form for updating a user's lens """
    name = StringField('Name',
                       validators=[DataRequired(), Length(min=1, max=64)])
    shutter = SelectField('Integrated Shutter',
                          validators=[Optional()],
                          choices=[('No', 'No'),
                                   ('Yes', 'Yes')])

class LensShutterSpeedsForm(FlaskForm):
    """ Form for putting in shutter speed tests for a lens """
    speed = IntegerField('Rated Speed',
                         validators=[DataRequired(),
                                     NumberRange(min=1, max=1000)])
    measuredSpeedMicroseconds = IntegerField('Measured Speed (microseconds)',
                                             validators=[DataRequired(),
                                                         NumberRange(min=1,
                                                                     max=64000000)])

class HolderForm(FlaskForm):
    """ Form for updating a user's film holder """
    name = StringField('Name',
                       validators=[DataRequired(), Length(min=1, max=64)])
    size = SelectField('Size',
                       validators=[DataRequired()],
                       choices=[('4x5', '4x5'),
                                ('5x7', '5x7'),
                                ('8x10', '8x10'),
                                ('11x14', '11x14')])
    status = SelectField('Status',
                       validators=[DataRequired()],
                       choices=[('Active', 'Active'),
                                ('Retired', 'Retired')])
    filmTypeID = SelectField('Film',
                             validators=[Optional()],
                             coerce=int)
    iso = IntegerField('Shot ISO', validators=[NumberRange(min=0, max=65535),
                                               Optional()])
    compensation = IntegerField('Compensation',
                                validators=[NumberRange(min=-64, max=64),
                                            Optional()])
    notes = TextAreaField('Notes',
                          validators=[Optional()],
                          filters=[lambda x: x or None])

    def populate_select_fields(self, connection):
        """ Helper function to populate select fields """
        self.filmTypeID.choices = optional_choices("None", get_film_types(connection))

@app.route('/gear', methods=['GET'])
@login_required
def gear():
    """ Gear index page """
    connection = engine.connect()
    transaction = connection.begin()
    transaction.commit()
    return render_template('/gear/index.html')

@app.route('/gear/filters', methods=['GET', 'POST'])
@login_required
def user_filters():
    """ Manage user's lens filters """
    connection = engine.connect()
    transaction = connection.begin()
    userID = current_user.get_id()
    filter_form = FilterForm()

    if request.method == 'POST':
        # Filters
        if request.form['button'] == 'addFilter':
            nextFilterID = next_id(connection, 'filterID', 'Filters')
            qry = text("""INSERT INTO Filters
                (userID, filterID, name, code, factor, ev)
                VALUES (:userID, :filterID, :name, :code, :factor, :ev)""")
            insert(connection, qry, "Filters",
                   userID=userID,
                   filterID=nextFilterID,
                   name=filter_form.name.data,
                   code=filter_form.code.data,
                   factor=filter_form.factor.data,
                   ev=filter_form.ev.data)

        if request.form['button'] == 'deleteFilter':
            qry = text("""DELETE FROM Filters
                WHERE userID = :userID
                AND filterID = :filterID""")
            delete(connection, qry, "Filter",
                   userID=userID,
                   filterID=int(request.form['filterID']))

    qry = text("""SELECT filterID, name, code, factor, ev
        FROM Filters
        WHERE userID = :userID ORDER BY name""")
    filters = connection.execute(qry, userID=current_user.get_id()).fetchall()

    transaction.commit()
    return render_template('/gear/filters.html',
                           filter_form=filter_form,
                           filters=filters)

@app.route('/gear/cameras', methods=['GET', 'POST'])
@login_required
def user_cameras():
    """ Manage a user's cameras """
    connection = engine.connect()
    transaction = connection.begin()
    userID = current_user.get_id()
    camera_form = CameraForm()
    camera_lens_form = CameraLensForm()

    if request.method == 'POST':
        # Camera
        if request.form['button'] == 'addCamera':
            app.logger.debug('Add Camera')
            nextCameraID = next_id(connection, 'cameraID', 'Cameras')
            qry = text("""INSERT INTO Cameras
                (cameraID, userID, name, filmSize) VALUES (:cameraID, :userID, :name, :filmSize)""")
            insert(connection, qry, "Camera",
                   cameraID=nextCameraID,
                   userID=int(current_user.get_id()),
                   name=camera_form.name.data,
                   filmSize=camera_form.filmSize.data)

        # Camera Lenses
        if request.form['button'] == 'addCameraLens':
            nextLensID = next_id(connection, 'lensID', 'Lenses')
            qry = text("""INSERT INTO Lenses
                (lensID, userID, name, shutter)
                VALUES (:lensID, :userID, :name, :shutter)""")
            insert(connection, qry, "Lens",
                   lensID=nextLensID,
                   userID=userID,
                   name=camera_lens_form.name.data,
                   shutter=camera_lens_form.shutter.data)

        if request.form['button'] == 'deleteCameraLens':
            qry = text("""DELETE FROM Lenses
                WHERE userID = :userID
                AND lensID = :lensID""")
            delete(connection, qry, "Lens",
                   userID=userID,
                   lensID=int(request.form['lensID']))

    qry = text("""SELECT cameraID, name, filmSize, status
        FROM Cameras
        WHERE userID = :userID ORDER BY filmSize, name""")
    cameras = connection.execute(qry, userID=userID).fetchall()

    qry = text("""SELECT lensID, name, shutter
        FROM Lenses
        WHERE userID = :userID ORDER BY name""")
    cameraLenses = connection.execute(qry, userID=userID).fetchall()

    transaction.commit()
    return render_template('/gear/cameras.html',
                           camera_form=camera_form,
                           camera_lens_form=camera_lens_form,
                           cameras=cameras,
                           cameraLenses=cameraLenses)

@app.route('/gear/camera/<int:cameraID>', methods=['GET', 'POST'])
@login_required
def user_camera(cameraID):
    """ Manage a specific camera """
    connection = engine.connect()
    transaction = connection.begin()
    userID = current_user.get_id()

    if request.method == 'POST':
        if request.form['button'] == 'editCamera':
            camera_form = CameraForm()
            qry = text("""UPDATE Cameras
                SET name = :name,
                    filmSize = :filmSize,
                    status = :status
                WHERE userID = :userID
                AND cameraID = :cameraID""")
            connection.execute(qry,
                               name=camera_form.name.data,
                               filmSize=camera_form.filmSize.data,
                               status=camera_form.status.data,
                               userID=userID,
                               cameraID=cameraID)

            # Remove and repopulate lenses based on selection
            qry = text("""DELETE FROM CameraLenses
                WHERE cameraID = :cameraID
                AND userID = :userID""")
            connection.execute(qry, cameraID=cameraID, userID=userID)

            qry = text("""INSERT INTO CameraLenses
                (userID, cameraID, lensID)
                VALUES (:userID, :cameraID, :lensID)""")
            for lensID in request.form.getlist('lenses'):
                connection.execute(qry,
                                   userID=userID,
                                   cameraID=cameraID,
                                   lensID=lensID)

    qry = text("""SELECT cameraID, name, filmSize
        FROM Cameras
        WHERE userID = :userID
        AND cameraID = :cameraID""")
    camera = connection.execute(qry,
                                userID=userID,
                                cameraID=cameraID).fetchone()

    qry = text("""SELECT lensID, name FROM Lenses
        WHERE userID = :userID""")
    lenses = connection.execute(qry, userID=userID).fetchall()

    qry = text("""SELECT CameraLenses.lensID AS lensID, name FROM CameraLenses
        JOIN Lenses ON Lenses.lensID = CameraLenses.lensID
            AND Lenses.userID = CameraLenses.userID
        WHERE CameraLenses.userID = :userID
        AND cameraID = :cameraID""")
    camera_lenses = connection.execute(qry,
                                       userID=userID,
                                       cameraID=cameraID).fetchall()

    camera_form = CameraForm(data=camera)
    camera_form.populate_select_fields(connection)
    camera_form.populate_lens_selections(camera_lenses)
    transaction.commit()

    if request.args.get('print'):
        template = '/gear/camera-print.html'
    else:
        template = '/gear/camera.html'

    return render_template(template,
                           camera_form=camera_form,
                           camera=camera,
                           camera_lenses=camera_lenses,
                           lenses=lenses)

@app.route('/gear/lens/<int:lensID>', methods=['GET', 'POST'])
@login_required
def user_lens(lensID):
    """ Manage a specific lens """
    connection = engine.connect()
    transaction = connection.begin()
    userID = current_user.get_id()
    shutter_speed_form = LensShutterSpeedsForm()

    if request.method == 'POST':
        if request.form['button'] == 'addSpeed':
            if shutter_speed_form.validate_on_submit():
                qry = text("""REPLACE INTO LensShutterSpeeds
                    (userID, lensID, speed, measuredSpeedMicroseconds)
                    VALUES (:userID, :lensID, :speed, :measuredSpeedMicroseconds)""")
                # pylint: disable=line-too-long
                # Haven't found a great way to format this without it being
                # more ugly.
                connection.execute(qry,
                                   speed=shutter_speed_form.speed.data,
                                   measuredSpeedMicroseconds=shutter_speed_form.measuredSpeedMicroseconds.data,
                                   userID=userID,
                                   lensID=lensID)
        if request.form['button'] == 'deleteSpeed':
            qry = text("""DELETE FROM LensShutterSpeeds
                WHERE userID = :userID
                AND lensID = :lensID
                AND speed = :speed""")
            connection.execute(qry,
                               userID=userID,
                               lensID=lensID,
                               speed=shutter_speed_form.speed.data)

    qry = text("""SELECT lensID, name, shutter
        FROM Lenses
        WHERE userID = :userID
        AND lensID = :lensID""")
    lens = connection.execute(qry,
                              userID=userID,
                              lensID=lensID).fetchone()

    qry = text("""SELECT speed, measuredSpeed,
        idealSpeedMicroseconds, measuredSpeedMicroseconds,
        differenceStops
        FROM LensShutterSpeeds
        WHERE userID = :userID
        AND lensID = :lensID""")
    shutter_speeds = connection.execute(qry,
                                        userID=userID,
                                        lensID=lensID).fetchall()
    transaction.commit()

    if request.args.get('print'):
        template = '/gear/lens-print.html'
    else:
        template = '/gear/lens.html'

    return render_template(template,
                           lens=lens,
                           shutter_speeds=shutter_speeds,
                           shutter_speed_form=shutter_speed_form)

@app.route('/gear/holders', methods=['GET', 'POST'])
@login_required
def user_holders():
    """ Manage holders """
    connection = engine.connect()
    transaction = connection.begin()
    userID = current_user.get_id()
    form = HolderForm()

    if request.method == 'POST':
        if request.form['button'] == 'addHolder':
            nextHolderID = next_id(connection, 'holderID', 'Holders')
            qry = text("""INSERT INTO Holders
                (userID, holderID, name, size, notes)
                VALUES (:userID, :holderID, :name, :size, :notes)""")
            connection.execute(qry,
                               userID=userID,
                               holderID=nextHolderID,
                               name=form.name.data,
                               size=form.size.data,
                               notes=form.notes.data)
    form.populate_select_fields(connection)
    transaction.commit()

    if request.args.get('print'):
        template = '/gear/holders-print.html'
    else:
        template = '/gear/holders.html'

    return render_template(template, form=form)

@app.route('/gear/holders/<int:holderID>', methods=['GET', 'POST'])
@login_required
def user_holder(holderID):
    """ Manage a film holder """
    connection = engine.connect()
    transaction = connection.begin()
    userID = current_user.get_id()

    if request.method == 'POST':
        form = HolderForm()
        if request.form['button'] == 'updateHolder':
            qry = text("""UPDATE Holders
                SET name = :name, size = :size, status = :status,
                filmTypeID = :filmTypeID,
                iso = :iso, compensation = :compensation, notes = :notes
                WHERE userID = :userID
                AND holderID = :holderID""")
            connection.execute(qry,
                               name=form.name.data,
                               size=form.size.data,
                               status=form.status.data,
                               filmTypeID=zero_to_none(form.filmTypeID.data),
                               iso=form.iso.data,
                               compensation=form.compensation.data,
                               notes=form.notes.data,
                               userID=userID,
                               holderID=holderID)
        if request.form['button'] == 'loadHolder':
            qry = text("""UPDATE Holders
                SET name = :name, size = :size, filmTypeID = :filmTypeID,
                iso = :iso, compensation = :compensation, notes = :notes,
                loaded = NOW()
                WHERE userID = :userID
                AND holderID = :holderID""")
            connection.execute(qry,
                               name=form.name.data,
                               size=form.size.data,
                               filmTypeID=zero_to_none(form.filmTypeID.data),
                               iso=form.iso.data,
                               compensation=form.compensation.data,
                               notes=form.notes.data,
                               userID=userID,
                               holderID=holderID)
        transaction.commit()
        return redirect("/gear/holders")

    qry = text("""SELECT holderID, Holders.name, size,
        IF(exposed, "Exposed",
            IF(loaded, "Loaded", "Unloaded")) AS state,
        status,
        loaded, unloaded, exposed,
        Holders.filmTypeID, Holders.iso, FilmTypes.name AS filmName,
        FilmTypes.iso AS filmISO, compensation, notes
        FROM Holders
        LEFT OUTER JOIN FilmTypes ON FilmTypes.filmTypeID = Holders.filmTypeID
            AND FilmTypes.userID = Holders.userID
        WHERE Holders.userID = :userID
        AND holderID = :holderID""")

    holder = connection.execute(qry,
                                userID=userID,
                                holderID=holderID).fetchone()

    qry = text("""SELECT Exposures.filmID, title, exposureNumber,
        fileDate, Projects.projectID, binderID
        FROM Exposures
        JOIN Films ON Films.filmID = Exposures.filmID
            AND Films.userID = Exposures.userID
        JOIN Projects ON Projects.projectID = Films.projectID
            AND Projects.userID = Films.userID
        WHERE Exposures.userID = :userID
        AND holderID = :holderID""")

    exposures = connection.execute(qry,
                                   userID=userID,
                                   holderID=holderID).fetchall()
    form = HolderForm(data=holder)
    form.populate_select_fields(connection)
    transaction.commit()

    return render_template('/gear/holder.html',
                           form=form,
                           holder=holder,
                           exposures=exposures)

@app.route('/gear/enlargers', methods=['GET', 'POST'])
@login_required
def user_enlargers():
    """ Manage user's enlargers """
    connection = engine.connect()
    transaction = connection.begin()
    userID = current_user.get_id()

    enlarger_lens_form = EnlargerLensForm()
    enlarger_form = EnlargerForm()

    if request.method == 'POST':
        app.logger.debug('POST')
        # Enlarger Lenses
        if request.form['button'] == 'addEnlargerLens':
            nextEnlargerLensID = next_id(connection, 'enlargerLensID', 'EnlargerLenses')
            qry = text("""INSERT INTO EnlargerLenses
                (enlargerLensID, userID, name)
                VALUES (:enlargerLensID, :userID, :name)""")
            insert(connection, qry, "Enlarger Lens",
                   enlargerLensID=nextEnlargerLensID,
                   userID=userID,
                   name=enlarger_lens_form.name.data)
        if request.form['button'] == 'deleteEnlargerLens':
            qry = text("""DELETE FROM EnlargerLenses
                WHERE userID = :userID
                AND enlargerLensID = :enlargerLensID""")
            connection.execute(qry,
                               userID=userID,
                               enlargerLensID=int(request.form['enlargerLensID']))

        if request.form['button'] == 'addEnlarger':
            nextEnlargerID = next_id(connection, 'enlargerID', 'Enlargers')
            qry = text("""INSERT INTO Enlargers
                (userID, enlargerID, name, type, lightsource, wattage, temperature, notes)
                VALUES (:userID, :enlargerID, :name, :type, :lightsource, :wattage,
                    :temperature, :notes)""")
            connection.execute(qry,
                               userID=userID,
                               enlargerID=nextEnlargerID,
                               name=enlarger_form.name.data,
                               type=enlarger_form.type.data,
                               lightsource=enlarger_form.lightsource.data,
                               wattage=enlarger_form.wattage.data,
                               temperature=enlarger_form.temperature.data,
                               notes=enlarger_form.notes.data)
        if request.form['button'] == 'deleteEnlarger':
            qry = text("""DELETE FROM Enlargers
                WHERE userID = :userID
                AND enlargerID = :enlargerID""")
            connection.execute(qry,
                               userID=userID,
                               enlargerID=int(request.form['enlargerID']))

    qry = text("""SELECT enlargerLensID, name
        FROM EnlargerLenses
        WHERE userID = :userID ORDER BY name""")
    enlargerLenses = connection.execute(qry,
                                        userID=current_user.get_id()).fetchall()

    qry = text("""SELECT enlargerID, name, type, lightsource, wattage,
        temperature, notes
        FROM Enlargers
        WHERE userID = :userID ORDER BY name""")
    enlargers = connection.execute(qry, userID=current_user.get_id()).fetchall()

    transaction.commit()
    return render_template('/gear/enlargers.html',
                           enlarger_lens_form=enlarger_lens_form,
                           enlarger_form=enlarger_form,
                           enlargerLenses=enlargerLenses,
                           enlargers=enlargers)
