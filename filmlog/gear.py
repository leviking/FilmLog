from flask import request, render_template, redirect, url_for, Response, session, abort, send_from_directory
from sqlalchemy.sql import select, text, func
import os, re

from flask_login import LoginManager, login_required, current_user, login_user, UserMixin

# Forms
from flask_wtf import FlaskForm
from wtforms import Form, StringField, DateField, SelectField, IntegerField, \
    TextAreaField, DecimalField, SelectMultipleField, BooleanField
from wtforms.validators import DataRequired, Optional, Length, NumberRange
from wtforms import widgets

from filmlog import app
from filmlog import database, engine
from filmlog.functions import next_id, insert, delete, optional_choices, get_film_types
from filmlog.classes import MultiCheckboxField

def get_lenses(connection):
    userID = current_user.get_id()
    qry = text("""SELECT lensID, name
        FROM Lenses
        WHERE userID = :userID""")
    return connection.execute(qry,
        userID = userID).fetchall()

class CameraForm(FlaskForm):
    name = StringField('Name',
        validators=[DataRequired(), Length(min=1, max=64)])
    filmSize = SelectField('Film Size',
        validators=[DataRequired()],
        choices=[
            ('35mm', '35mm'),
            ('120', '120'),
            ('220', '220'),
            ('4x5', '4x5'),
            ('8x10', '8x10')])
    lenses = MultiCheckboxField('Lenses',
        validators=[Optional()])

    def populate_select_fields(self, connection):
        self.connection = connection
        self.lenses.choices = get_lenses(connection)

    def populate_lens_selections(self, lenses):
        selected_lenses = []
        for lens in lenses:
            selected_lenses.append(lens.lensID)
        self.lenses.process_data(selected_lenses)

class FilterForm(FlaskForm):
    name = StringField('Name',
        validators=[DataRequired(), Length(min=1, max=64)])
    code = StringField('Code',
        validators=[DataRequired(), Length(min=1, max=8)])
    factor = DecimalField('Factor', places=1,
        validators=[DataRequired()])
    ev = DecimalField('EV', places=1,
        validators=[DataRequired()])

class CameraLensForm(FlaskForm):
    name = StringField('Name',
        validators=[DataRequired(), Length(min=1, max=64)])

class EnlargerLensForm(FlaskForm):
    name = StringField('Name',
        validators=[DataRequired(), Length(min=1, max=64)])

class EnlargerForm(FlaskForm):
    name = StringField('Name',
        validators=[DataRequired(), Length(min=1, max=64)])
    type = SelectField('Type',
        validators=[DataRequired()],
        choices=[
            ('Condenser', 'Condenser'),
            ('Diffuser', 'Diffuser')])
    lightsource = SelectField('Type',
        validators=[DataRequired()],
        choices=[
            ('LED', 'LED'),
            ('Incandescent', 'Incandescent')])
    wattage = IntegerField('Wattage',
            validators=[NumberRange(min=0,max=65535),
                        Optional()])
    temperature = IntegerField('Temperature (K)',
            validators=[NumberRange(min=0,max=65535),
                        Optional()])
    notes = TextAreaField('Notes',
        validators=[Optional()],
        filters = [lambda x: x or None])

class HolderForm(FlaskForm):
    name = StringField('Name',
        validators=[DataRequired(), Length(min=1, max=64)])
    size = SelectField('Size',
        validators=[DataRequired()],
        choices=[
            ('4x5', '4x5'),
            ('5x7', '5x7'),
            ('8x10', '8x10'),
            ('11x14', '11x14')])
    filmTypeID = SelectField('Film',
        validators=[Optional()],
        coerce=int)
    iso = IntegerField('Shot ISO',
            validators=[NumberRange(min=0,max=65535),
                        Optional()])
    compensation = IntegerField('Compensation',
            validators=[NumberRange(min=-64,max=64),
                        Optional()])
    notes = TextAreaField('Notes',
        validators=[Optional()],
        filters = [lambda x: x or None])

    def populate_select_fields(self, connection):
        self.connection = connection
        self.filmTypeID.choices = optional_choices("None", get_film_types(connection))

@app.route('/gear',  methods = ['GET', 'POST'])
@login_required
def gear():
    connection = engine.connect()
    transaction = connection.begin()
    userID = current_user.get_id()

    transaction.commit()
    return render_template('/gear/index.html')

@app.route('/gear/enlargers',  methods = ['GET', 'POST'])
@login_required
def enlargers():
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
                enlargerLensID = nextEnlargerLensID,
                userID = userID,
                name = enlarger_lens_form.name.data)
        if request.form['button'] == 'deleteEnlargerLens':
            qry = text("""DELETE FROM EnlargerLenses
                WHERE userID = :userID
                AND enlargerLensID = :enlargerLensID""")
            connection.execute(qry,
                userID = userID,
                enlargerLensID = int(request.form['enlargerLensID']))

        if request.form['button'] == 'addEnlarger':
            nextEnlargerID = next_id(connection, 'enlargerID', 'Enlargers')
            qry = text("""INSERT INTO Enlargers
                (userID, enlargerID, name, type, lightsource, wattage, temperature, notes)
                VALUES (:userID, :enlargerID, :name, :type, :lightsource, :wattage,
                    :temperature, :notes)""")
            connection.execute(qry,
                userID = userID,
                enlargerID = nextEnlargerID,
                name = enlarger_form.name.data,
                type = enlarger_form.type.data,
                lightsource = enlarger_form.lightsource.data,
                wattage = enlarger_form.wattage.data,
                temperature = enlarger_form.temperature.data,
                notes = enlarger_form.notes.data)
        if request.form['button'] == 'deleteEnlarger':
            qry = text("""DELETE FROM Enlargers
                WHERE userID = :userID
                AND enlargerID = :enlargerID""")
            connection.execute(qry,
                userID = userID,
                enlargerID = int(request.form['enlargerID']))

    qry = text("""SELECT enlargerLensID, name
        FROM EnlargerLenses
        WHERE userID = :userID ORDER BY name""")
    enlargerLenses = connection.execute(qry, userID = current_user.get_id()).fetchall()

    qry = text("""SELECT enlargerID, name, type, lightsource, wattage,
        temperature, notes
        FROM Enlargers
        WHERE userID = :userID ORDER BY name""")
    enlargers = connection.execute(qry, userID = current_user.get_id()).fetchall()

    transaction.commit()
    return render_template('/gear/enlargers.html',
        enlarger_lens_form = enlarger_lens_form,
        enlarger_form = enlarger_form,
        enlargerLenses = enlargerLenses,
        enlargers = enlargers)

@app.route('/gear/filters',  methods = ['GET', 'POST'])
@login_required
def filters():
    connection = engine.connect()
    transaction = connection.begin()
    userID = current_user.get_id()
    filter_form = FilterForm()

    if request.method == 'POST':
        app.logger.debug('POST')
        # Filters
        if request.form['button'] == 'addFilter':
            nextFilterID = next_id(connection, 'filterID', 'Filters')
            qry = text("""INSERT INTO Filters
                (userID, filterID, name, code, factor, ev)
                VALUES (:userID, :filterID, :name, :code, :factor, :ev)""")
            insert(connection, qry, "Filters",
                userID = userID,
                filterID = nextFilterID,
                name = filter_form.name.data,
                code = filter_form.code.data,
                factor = filter_form.factor.data,
                ev = filter_form.ev.data)

        if request.form['button'] == 'deleteFilter':
            qry = text("""DELETE FROM Filters
                WHERE userID = :userID
                AND filterID = :filterID""")
            delete(connection, qry, "Filter",
                userID = userID,
                filterID = int(request.form['filterID']))

    qry = text("""SELECT filterID, name, code, factor, ev
        FROM Filters
        WHERE userID = :userID ORDER BY name""")
    filters = connection.execute(qry, userID = current_user.get_id()).fetchall()

    transaction.commit()
    return render_template('/gear/filters.html',
        filter_form = filter_form,
        filters=filters)

@app.route('/gear/cameras',  methods = ['GET', 'POST'])
@login_required
def cameras():
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
                cameraID = nextCameraID,
                userID = int(current_user.get_id()),
                name = camera_form.name.data,
                filmSize = camera_form.filmSize.data)

        # Camera Lenses
        if request.form['button'] == 'addCameraLens':
            nextLensID = next_id(connection, 'lensID', 'Lenses')
            qry = text("""INSERT INTO Lenses
                (lensID, userID, name)
                VALUES (:lensID, :userID, :name)""")
            insert(connection, qry, "Lens",
                lensID = nextLensID,
                userID = userID,
                name = camera_lens_form.name.data)

        if request.form['button'] == 'deleteCameraLens':
            qry = text("""DELETE FROM Lenses
                WHERE userID = :userID
                AND lensID = :lensID""")
            delete(connection, qry, "Lens",
                userID = userID,
                lensID = int(request.form['lensID']))

    qry = text("""SELECT cameraID, name, filmSize
        FROM Cameras
        WHERE userID = :userID ORDER BY filmSize, name""")
    cameras = connection.execute(qry, userID = userID).fetchall()

    qry = text("""SELECT lensID, name
        FROM Lenses
        WHERE userID = :userID ORDER BY name""")
    cameraLenses = connection.execute(qry, userID = userID).fetchall()

    transaction.commit()
    return render_template('/gear/cameras.html',
        camera_form = camera_form,
        camera_lens_form = camera_lens_form,
        cameras=cameras,
        cameraLenses = cameraLenses)

@app.route('/gear/camera/<int:cameraID>',  methods = ['GET', 'POST'])
@login_required
def camera(cameraID):
    connection = engine.connect()
    transaction = connection.begin()
    userID = current_user.get_id()

    if request.method == 'POST':
        if request.form['button'] == 'editCamera':
            camera_form = CameraForm()
            qry = text("""UPDATE Cameras
                SET name = :name,
                    filmSize = :filmSize
                WHERE uintserID = :userID
                AND cameraID = :cameraID""")
            connection.execute(qry,
                name = camera_form.name.data,
                filmSize = camera_form.filmSize.data,
                userID = userID,
                cameraID = cameraID)

            # Remove and repopulate lenses based on selection
            qry = text("""DELETE FROM CameraLenses
                WHERE cameraID = :cameraID
                AND userID = :userID""")
            connection.execute(qry, cameraID = cameraID,
                userID = userID)

            qry = text("""INSERT INTO CameraLenses
                (userID, cameraID, lensID)
                VALUES (:userID, :cameraID, :lensID)""")
            for lensID in request.form.getlist('lenses'):
                connection.execute(qry,
                    userID = userID,
                    cameraID = cameraID,
                    lensID = lensID)

    qry = text("""SELECT cameraID, name, filmSize
        FROM Cameras
        WHERE userID = :userID
        AND cameraID = :cameraID""")
    camera = connection.execute(qry,
        userID = userID,
        cameraID = cameraID).fetchone()

    qry = text("""SELECT lensID, name FROM Lenses
        WHERE userID = :userID""")
    lenses = connection.execute(qry,
        userID = userID).fetchall()

    qry = text("""SELECT CameraLenses.lensID AS lensID, name FROM CameraLenses
        JOIN Lenses ON Lenses.lensID = CameraLenses.lensID
        WHERE CameraLenses.userID = :userID
        AND cameraID = :cameraID""")
    camera_lenses = connection.execute(qry,
        userID = userID,
        cameraID = cameraID).fetchall()

    camera_form = CameraForm(data=camera)
    camera_form.populate_select_fields(connection)
    camera_form.populate_lens_selections(camera_lenses)
    transaction.commit()
    return render_template('/gear/camera.html',
        camera_form = camera_form,
        camera = camera,
        camera_lenses = camera_lenses,
        lenses = lenses)

@app.route('/gear/holders',  methods = ['GET', 'POST'])
@login_required
def holders():
    connection = engine.connect()
    transaction = connection.begin()
    userID = current_user.get_id()
    form = HolderForm()

    if request.method == 'POST':
        if request.form['button'] == 'Unload':
            qry = text("""UPDATE Holders
                SET loaded = NULL, exposed = NULL, unloaded = NOW()
                WHERE userID = :userID AND holderID = :holderID""")
            connection.execute(qry,
                userID = userID,
                holderID = int(request.form['holderID']))

        if request.form['button'] == 'Load':
            return redirect("/gear/holders/" + request.form['holderID'])

        if request.form['button'] == 'Reload':
            qry = text("""UPDATE Holders
                SET loaded = NOW(), exposed = NULL, unloaded = NULL
                WHERE userID = :userID AND holderID = :holderID""")
            connection.execute(qry,
                userID = userID,
                holderID = int(request.form['holderID']))

        if request.form['button'] == 'Expose':
            qry = text("""UPDATE Holders
                SET exposed = NOW()
                WHERE userID = :userID AND holderID = :holderID""")
            connection.execute(qry,
                userID = userID,
                holderID = int(request.form['holderID']))

        if request.form['button'] == 'addHolder':
            nextHolderID = next_id(connection, 'holderID', 'Holders')
            qry = text("""INSERT INTO Holders
                (userID, holderID, name, size, notes)
                VALUES (:userID, :holderID, :name, :size, :notes)""")
            connection.execute(qry,
                userID = userID,
                holderID = nextHolderID,
                name = form.name.data,
                size = form.size.data,
                notes = form.notes.data)

    form.populate_select_fields(connection)

    qry = text("""SELECT holderID, Holders.name, size,
        IF(exposed, "Exposed",
            IF(loaded, "Loaded", "Unloaded")) AS state,
        Holders.filmTypeID, Holders.iso, brand AS filmBrand, FilmTypes.name AS filmName,
        FilmTypes.iso AS filmISO, compensation, notes
        FROM Holders
        LEFT OUTER JOIN FilmTypes ON FilmTypes.filmTypeID = Holders.filmTypeID
        LEFT OUTER JOIN FilmBrands ON FilmBrands.filmBrandID = FilmTypes.filmBrandID
        WHERE userID = :userID""")
    holders = connection.execute(qry,
        userID = userID)
    transaction.commit()

    return render_template('/gear/holders.html',
        form = form,
        holders = holders)

@app.route('/gear/holders/<int:holderID>',  methods = ['GET', 'POST'])
@login_required
def holder(holderID):
    connection = engine.connect()
    transaction = connection.begin()
    userID = current_user.get_id()

    if request.method == 'POST':
        form = HolderForm()
        if request.form['button'] == 'updateHolder':
            qry = text("""UPDATE Holders
                SET name = :name, size = :size, filmTypeID = :filmTypeID,
                iso = :iso, compensation = :compensation, notes = :notes
                WHERE userID = :userID
                AND holderID = :holderID""")
            connection.execute(qry,
                name = form.name.data,
                size = form.size.data,
                filmTypeID = form.filmTypeID.data,
                iso = form.iso.data,
                compensation = form.compensation.data,
                notes = form.notes.data,
                userID = userID,
                holderID = holderID)

    qry = text("""SELECT holderID, Holders.name, size,
        IF(exposed, "Exposed",
            IF(loaded, "Loaded", "Unloaded")) AS state,
        loaded, unloaded, exposed,
        Holders.filmTypeID, Holders.iso, brand AS filmBrand, FilmTypes.name AS filmName,
        FilmTypes.iso AS filmISO, compensation, notes
        FROM Holders
        LEFT OUTER JOIN FilmTypes ON FilmTypes.filmTypeID = Holders.filmTypeID
        LEFT OUTER JOIN FilmBrands ON FilmBrands.filmBrandID = FilmTypes.filmBrandID
        WHERE userID = :userID
        AND holderID = :holderID""")

    holder = connection.execute(qry,
        userID = userID, holderID = holderID).fetchone()
    form = HolderForm(data=holder)
    form.populate_select_fields(connection)
    transaction.commit()

    return render_template('/gear/holder.html',
        form = form, holder = holder)
