from flask import request, render_template, redirect, url_for, flash, abort
from sqlalchemy.sql import select, text, func
import os, re

from flask_login import LoginManager, login_required, current_user, login_user, UserMixin

# Forms
from flask_wtf import FlaskForm
from wtforms import Form, StringField, IntegerField, SelectField, RadioField, \
    DecimalField, TextAreaField, FileField, validators
from wtforms.validators import DataRequired, Optional, NumberRange, ValidationError
from flask_wtf.file import FileAllowed

from filmlog import app
from filmlog import database, engine
from filmlog import functions
from filmlog import files

from filmlog.functions import optional_choices, zero_to_none, insert, result_to_dict

engine = database.engine

## Functions
def get_paper_filters(connection):
    qry = text("""SELECT paperFilterID, name FROM PaperFilters""")
    return connection.execute(qry).fetchall()

def get_papers(connection):
    # Get info for adding/updating contact sheet
    qry = text("""SELECT paperID,
        CONCAT(PaperBrands.name, " ", Papers.name) AS name
        FROM Papers
        JOIN PaperBrands ON PaperBrands.paperBrandID = Papers.paperBrandID""")
    return connection.execute(qry).fetchall()

def get_enlarger_lenses(connection):
    userID = current_user.get_id()
    qry = text("""SELECT enlargerLensID, name
        FROM EnlargerLenses
        WHERE userID = :userID""")
    return connection.execute(qry, userID = userID).fetchall()

def get_enlargers(connection):
    userID = current_user.get_id()
    qry = text("""SELECT enlargerID, name
        FROM Enlargers
        WHERE userID = :userID""")
    return connection.execute(qry, userID = userID).fetchall()

def get_exposures(connection, filmID):
    userID = current_user.get_id()
    qry = text("""SELECT exposureNumber AS exposureNumber,
        exposureNumber AS subject
        FROM Exposures
        WHERE userID = :userID
        AND filmID = :filmID""")
    return connection.execute(qry,
        userID = userID, filmID = filmID).fetchall()

def time_to_seconds(time):
    # If time is in MM:SS format, calculate the raw seconds
    # Otherwise just return the time as-is
    if time:
        if ':' not in time:
            if int(time) > 0:
                return int(time)
        else:
            m, s = time.split(':')
            return int(m) * 60 + int(s)
    raise ValidationError('Time in wrong format, it should be MM:SS.')

def validate_exposure_time(form, field):
    try:
        time_to_seconds(field.data)
    except Exception:
        raise ValidationError('Time in wrong format, it should be in MM:SS or in seconds.')

def seconds_to_time(seconds):
    return str(int(seconds / 60)) + ":" + str(int(seconds % 60))

## Classes
# Forms
class PrintForm(FlaskForm):
    exposureNumber = SelectField('Exposure #',
        validators=[DataRequired()],
        coerce=int)
    paperID = SelectField('Paper',
        validators=[Optional()],
        coerce=int)
    paperFilterID = SelectField('Filters',
        validators=[Optional()],
        coerce=int)
    printType = SelectField('Type',
        validators=[DataRequired()],
        choices=[('Enlargement', 'Enlargement'), ('Contact', 'Contact')])
    size = SelectField('Size',
        validators=[DataRequired()],
        choices=[('4x5', '4x5'), ('4x6', '4x6'), ('5x7', '5x7'), ('8x10', '8x10'), ('11x14', '11x14'), ('Other', 'Other')])
    enlargerLensID = SelectField('Enlarger Lens',
        validators=[Optional()],
        coerce=int)
    enlargerID = SelectField('Enlarger',
        validators=[Optional()],
        coerce=int)
    aperture = DecimalField('Aperture', places=1,
        validators=[Optional()])
    headHeight = IntegerField('Head Height',
        validators=[NumberRange(min=0,max=255),
                    Optional()])
    exposureTime = StringField('Exposure Time',
        validators=[DataRequired(), validate_exposure_time])
    notes = TextAreaField('Notes',
        validators=[Optional()],
        filters = [lambda x: x or None])

    file = FileField('File (JPG)',
        validators=[Optional(), FileAllowed(['jpg'], 'JPEGs Only')])

    def populate_select_fields(self, connection, filmID):
        self.connection = connection
        self.paperID.choices = optional_choices("None", get_papers(connection))
        self.paperFilterID.choices = optional_choices("None", get_paper_filters(connection))
        self.enlargerLensID.choices = optional_choices("None", get_enlarger_lenses(connection))
        self.enlargerID.choices = optional_choices("None", get_enlargers(connection))
        self.exposureNumber.choices = get_exposures(connection, filmID)

class ContactSheetForm(FlaskForm):
    paperID = SelectField('Paper',
        validators=[Optional()],
        coerce=int)
    paperFilterID = SelectField('Filters',
        validators=[Optional()],
        coerce=int)
    enlargerLensID = SelectField('Enlarger Lens',
        validators=[Optional()],
        coerce=int)
    enlargerID = SelectField('Enlarger',
        validators=[Optional()],
        coerce=int)
    aperture = DecimalField('Aperture', places=1,
        validators=[Optional()],
        filters = [lambda x: x or None])
    headHeight = IntegerField('Head Height',
        validators=[NumberRange(min=0,max=255),
                    Optional()],
        filters = [lambda x: x or None])
    exposureTime = StringField('Exposure Time',
        validators=[DataRequired(), validate_exposure_time])
    notes = TextAreaField('Notes',
        validators=[Optional()],
        filters = [lambda x: x or None])
    file = FileField('File (JPG)',
        validators=[Optional(), FileAllowed(['jpg'], 'JPEGs Only')])

    def populate_select_fields(self, connection):
        self.connection = connection
        self.paperID.choices = optional_choices("None", get_papers(connection))
        self.paperFilterID.choices = optional_choices("None", get_paper_filters(connection))
        self.enlargerLensID.choices = optional_choices("None", get_enlarger_lenses(connection))
        self.enlargerID.choices = optional_choices("None", get_enlargers(connection))

def check_for_print_file(connection, printID):
    userID = current_user.get_id()
    qry = text("""SELECT fileID FROM Prints
        WHERE printID = :printID AND userID = :userID""")
    result = connection.execute(qry,
        printID = printID,
        userID = userID).fetchone()
    if result:
        if result[0]:
            return int(result[0])
    return None

@app.route('/binders/<int:binderID>/projects/<int:projectID>/films/<int:filmID>/prints',  methods = ['POST', 'GET'])
@login_required
def prints(binderID, projectID, filmID):
    connection = engine.connect()
    transaction = connection.begin()
    userID = current_user.get_id()
    form = PrintForm()
    form.populate_select_fields(connection, filmID)

    if request.method == 'POST':
        if request.form['button'] == 'addPrint':
            if form.validate_on_submit():
                nextPrintID = functions.next_id(connection, 'printID', 'Prints')
                # If user included a file, let's upload it. Otherwise skip it.
                if form.file.data:
                    nextFileID = functions.next_id(connection, 'fileID', 'Files')
                    files.upload_file(request, connection, transaction, nextFileID)
                else:
                    nextFileID = None

                qry = text("""INSERT INTO Prints
                    (printID, filmID, exposureNumber, userID, paperID, paperFilterID,
                    enlargerLensID, enlargerID, fileID, aperture, headHeight, exposureTime, printType, size, notes)
                    VALUES (:printID, :filmID, :exposureNumber, :userID, :paperID,
                    :paperFilterID, :enlargerLensID, :enlargerID, :fileID, :aperture, :headHeight, :exposureTime,
                    :printType, :size, :notes)""")
                insert(connection, qry, "Print",
                    printID = nextPrintID,
                    filmID = filmID,
                    userID = userID,
                    fileID = nextFileID,
                    exposureNumber = form.exposureNumber.data,
                    paperID = zero_to_none(form.paperID.data),
                    paperFilterID = zero_to_none(form.paperFilterID.data),
                    enlargerLensID = zero_to_none(form.enlargerLensID.data),
                    enlargerID = zero_to_none(form.enlargerID.data),
                    aperture = form.aperture.data,
                    headHeight = form.headHeight.data,
                    exposureTime = time_to_seconds(form.exposureTime.data),
                    printType = form.printType.data,
                    size = form.size.data,
                    notes = form.notes.data)
    film = functions.get_film_details(connection, binderID, projectID, filmID)

    qry = text("""SELECT printID, exposureNumber, Papers.name AS paperName,
        PaperBrands.name AS paperBrand, PaperFilters.name AS paperFilterName,
        printType, size, aperture, headHeight, Prints.notes, fileID,
        EnlargerLenses.name AS lens,
        Enlargers.name AS enlarger,
        SECONDS_TO_DURATION(exposureTime) AS exposureTime
        FROM Prints
        LEFT OUTER JOIN Papers ON Papers.paperID = Prints.paperID
        LEFT OUTER JOIN PaperBrands ON PaperBrands.paperBrandID = Papers.paperBrandID
        LEFT OUTER JOIN PaperFilters ON PaperFilters.paperFilterID = Prints.paperFilterID
        LEFT OUTER JOIN EnlargerLenses ON EnlargerLenses.enlargerLensID = Prints.enlargerLensID
            AND EnlargerLenses.userID = Prints.userID
        LEFT OUTER JOIN Enlargers ON Enlargers.enlargerID = Prints.enlargerID
            AND Enlargers.userID = Prints.userID
        WHERE filmID = :filmID AND Prints.userID = :userID""")
    prints = connection.execute(qry,
        userID = userID,
        filmID = filmID)

    transaction.commit()
    return render_template('darkroom/prints.html',
        form = form,
        binderID=binderID,
        projectID=projectID,
        film=film,
        prints = prints,
        view='prints')

@app.route('/binders/<int:binderID>/projects/<int:projectID>/films/<int:filmID>/prints/<int:printID>',  methods = ['POST', 'GET'])
@login_required
def print_exposure(binderID, projectID, filmID, printID):
    connection = engine.connect()
    transaction = connection.begin()
    userID = current_user.get_id()
    form = PrintForm()
    form.populate_select_fields(connection, filmID)

    if request.method == 'POST':
        if request.form['button'] == 'deletePrint':
            fileID = check_for_print_file(connection, printID)
            qry = text("""DELETE FROM Prints
                WHERE printID = :printID
                AND userID = :userID""")
            connection.execute(qry,
                printID = printID,
                userID = userID)
            if fileID:
                files.delete_file(request, connection, transaction, fileID)
            transaction.commit()
            return redirect('/binders/' + str(binderID)
                + '/projects/' + str(projectID)
                + '/films/' + str(filmID)
                + '/prints')

        if request.form['button'] == 'updatePrint':
            if form.validate_on_submit():
                # See if there is a fileID
                fileID = check_for_print_file(connection, printID)
                # If the user has a file already, delete it first.
                # Otherwise treat it like a new file.
                if form.file.data:
                    if fileID:
                        app.logger.info('Replace File')
                        files.delete_file(request, connection, transaction, fileID)
                        files.upload_file(request, connection, transaction, fileID)
                    else:
                        app.logger.info('Brand New File')
                        fileID = functions.next_id(connection, 'fileID', 'Files')
                        files.upload_file(request, connection, transaction, fileID)
                qry = text("""REPLACE INTO Prints
                    (printID, filmID, exposureNumber, userID, paperID, paperFilterID,
                    enlargerLensID, enlargerID, fileID, aperture, headHeight, exposureTime, printType, size, notes)
                    VALUES (:printID, :filmID, :exposureNumber, :userID, :paperID,
                    :paperFilterID, :enlargerLensID, :enlargerID, :fileID, :aperture, :headHeight, :exposureTime,
                    :printType, :size, :notes)""")
                insert(connection, qry, "Print",
                    printID = printID,
                    filmID = filmID,
                    userID = userID,
                    fileID = fileID,
                    exposureNumber = form.exposureNumber.data,
                    paperID = zero_to_none(form.paperID.data),
                    paperFilterID = zero_to_none(form.paperFilterID.data),
                    enlargerLensID = zero_to_none(form.enlargerLensID.data),
                    enlargerID = zero_to_none(form.enlargerID.data),
                    aperture = form.aperture.data,
                    headHeight = form.headHeight.data,
                    exposureTime = time_to_seconds(form.exposureTime.data),
                    printType = form.printType.data,
                    size = form.size.data,
                    notes = form.notes.data)
                transaction.commit()
                return redirect('/binders/' + str(binderID)
                    + '/projects/' + str(projectID)
                    + '/films/' + str(filmID)
                    + '/prints')

    film = functions.get_film_details(connection, binderID, projectID, filmID)
    qry = text("""SELECT printID, exposureNumber, Papers.name AS paperName,
        Papers.paperID, PaperFilters.paperFilterID, EnlargerLenses.enlargerLensID,
        Enlargers.enlargerID,
        printType, size, aperture, headHeight, Prints.notes, fileID,
        SECONDS_TO_DURATION(exposureTime) AS exposureTime
        FROM Prints
        LEFT OUTER JOIN Papers ON Papers.paperID = Prints.paperID
        LEFT OUTER JOIN PaperBrands ON PaperBrands.paperBrandID = Papers.paperBrandID
        LEFT OUTER JOIN PaperFilters ON PaperFilters.paperFilterID = Prints.paperFilterID
        LEFT OUTER JOIN EnlargerLenses ON EnlargerLenses.enlargerLensID = Prints.enlargerLensID
            AND EnlargerLenses.userID = Prints.userID
        LEFT OUTER JOIN Enlargers ON Enlargers.enlargerID = Prints.enlargerID
            AND Enlargers.userID = Prints.userID
        WHERE Prints.userID = :userID
        AND Prints.printID = :printID""")
    print_details = connection.execute(qry,
        userID = userID,
        printID = printID).fetchone()
    transaction.commit()
    form = PrintForm(data=print_details)
    form.populate_select_fields(connection, filmID)
    return render_template('darkroom/edit-print.html',
        form = form,
        film = film,
        binderID = binderID,
        projectID = projectID,
        printID = printID,
        print_details = print_details,
        view = 'prints')

@app.route('/binders/<int:binderID>/projects/<int:projectID>/films/<int:filmID>/contactsheet',  methods = ['POST', 'GET'])
@login_required
def contactsheet(binderID, projectID, filmID):
    connection = engine.connect()
    transaction = connection.begin()
    userID = current_user.get_id()
    form = ContactSheetForm()
    form.populate_select_fields(connection)

    # Upload a new contact sheet
    if request.method == 'POST':
        # See if there is a contact sheet already
        qry = text("""SELECT fileID FROM ContactSheets
            WHERE filmID = :filmID AND userID = :userID""")
        result = connection.execute(qry,
            filmID = filmID,
            userID = userID).fetchone()
        if(result):
            fileID = int(result[0])
        else:
            fileID = None
        if request.form['button'] == 'deleteCS':
            qry = text("""DELETE FROM ContactSheets
                WHERE filmID = :filmID AND userID = :userID""")
            connection.execute(qry,
                filmID = filmID,
                userID = userID)
            if fileID:
                print fileID
                files.delete_file(request, connection, transaction, fileID)
        elif request.form['button'] == 'updateCS' and form.validate_on_submit():
            # If user included a file, let's upload it. Otherwise skip it.
            if 'file' in request.files:
                nextFileID = functions.next_id(connection, 'fileID', 'Files')
                files.upload_file(request, connection, transaction, nextFileID)
            # If we're updating an existing sheet and the user didn't upload
            # a new file, use the old one.
            else:
                nextFileID = fileID
            qry = text("""REPLACE INTO ContactSheets (filmID, userID, fileID, paperID, paperFilterID, enlargerLensID, enlargerID, aperture, headHeight, exposureTime, notes)
                VALUES (:filmID, :userID, :fileID, :paperID, :paperFilterID, :enlargerLensID, :enlargerID, :aperture, :headHeight, :exposureTime, :notes)""")
            connection.execute(qry,
                filmID = filmID,
                userID = userID,
                fileID = nextFileID,
                paperID = zero_to_none(form.paperID.data),
                paperFilterID = zero_to_none(form.paperFilterID.data),
                enlargerLensID = zero_to_none(form.enlargerLensID.data),
                enlargerID = zero_to_none(form.enlargerID.data),
                aperture = form.aperture.data,
                headHeight = form.headHeight.data,
                exposureTime = time_to_seconds(form.exposureTime.data),
                notes = form.notes.data)

    film = functions.get_film_details(connection, binderID, projectID, filmID)

    # Get contact sheet info
    qry = text("""SELECT fileID, Papers.name AS paperName,
        PaperBrands.name AS paperBrand, PaperFilters.name AS paperFilterName,
        EnlargerLenses.name AS lens, Enlargers.name AS enlarger,
        aperture, headHeight, ContactSheets.notes,
        ContactSheets.paperID AS paperID,
        ContactSheets.paperFilterID AS paperFilterID,
        ContactSheets.enlargerLensID AS enlargerLensID,
        SECONDS_TO_DURATION(exposureTime) AS exposureTime
        FROM ContactSheets
        LEFT OUTER JOIN Papers ON Papers.paperID = ContactSheets.paperID
        LEFT OUTER JOIN PaperBrands ON PaperBrands.paperBrandID = Papers.paperBrandID
        LEFT OUTER JOIN PaperFilters ON PaperFilters.paperFilterID = ContactSheets.paperFilterID
        LEFT OUTER JOIN EnlargerLenses ON EnlargerLenses.enlargerLensID = ContactSheets.enlargerLensID
            AND EnlargerLenses.userID = ContactSheets.userID
        LEFT OUTER JOIN Enlargers ON Enlargers.enlargerID = ContactSheets.enlargerID
            AND Enlargers.userID = ContactSheets.userID
        WHERE filmID = :filmID AND ContactSheets.userID = :userID""")
    contactSheet =  connection.execute(qry,
        userID = userID,
        binderID = binderID,
        filmID=filmID).fetchone()
    if contactSheet:
        app.logger.debug("Existing Contact Sheet")
        form = ContactSheetForm(data=contactSheet)
        form.populate_select_fields(connection)
    transaction.commit()
    return render_template('darkroom/contactsheet.html',
        binderID=binderID,
        projectID=projectID,
        film=film,
        contactSheet=contactSheet,
        form=form,
        view='contactsheet')
