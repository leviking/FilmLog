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
from filmlog import database
from filmlog.functions import next_id, insert
from filmlog.classes import MultiCheckboxField

engine = database.engine

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

@app.route('/gear',  methods = ['GET', 'POST'])
@login_required
def gear():
    connection = engine.connect()
    transaction = connection.begin()
    userID = current_user.get_id()
    camera_form = CameraForm()
    filter_form = FilterForm()
    enlarger_lens_form = EnlargerLensForm()
    camera_lens_form = CameraLensForm()

    if request.method == 'POST':
        app.logger.debug('POST')

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
                filmSize = camera_form.filmSize.data
                )

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
            connection.execute(qry,
                userID = userID,
                filterID = int(request.form['filterID']))

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
            connection.execute(qry,
                userID = userID,
                lensID = int(request.form['lensID']))

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

    qry = text("""SELECT cameraID, name, filmSize
        FROM Cameras
        WHERE userID = :userID ORDER BY filmSize, name""")
    cameras = connection.execute(qry, userID = userID).fetchall()

    qry = text("""SELECT lensID, name
        FROM Lenses
        WHERE userID = :userID ORDER BY name""")
    cameraLenses = connection.execute(qry, userID = userID).fetchall()

    qry = text("""SELECT filterID, name, code, factor, ev
        FROM Filters
        WHERE userID = :userID ORDER BY name""")
    filters = connection.execute(qry, userID = current_user.get_id()).fetchall()

    qry = text("""SELECT enlargerLensID, name
        FROM EnlargerLenses
        WHERE userID = :userID ORDER BY name""")
    enlargerLenses = connection.execute(qry, userID = current_user.get_id()).fetchall()

    transaction.commit()
    return render_template('/gear/index.html',
        camera_form = camera_form,
        filter_form = filter_form,
        camera_lens_form = camera_lens_form,
        enlarger_lens_form = enlarger_lens_form,
        cameras=cameras,
        filters=filters,
        cameraLenses = cameraLenses,
        enlargerLenses=enlargerLenses)


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
                WHERE userID = :userID
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
