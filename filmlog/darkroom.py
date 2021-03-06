""" Darkroom specific views (/darkroom) """
from sqlalchemy.sql import text
from flask import request, render_template, redirect
from flask_login import login_required, current_user

# Forms
from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed
from wtforms import StringField, IntegerField, SelectField, \
    DecimalField, TextAreaField, FileField
from wtforms.validators import DataRequired, Optional, NumberRange

# Filmlog
from filmlog import functions
from filmlog import files
from filmlog.config import app, engine
from filmlog.functions import optional_choices, zero_to_none, insert, \
                              get_enlargers, log

## Functions
def get_papers(connection):
    """ Helper function to get available papers """
    userID = current_user.get_id()
    qry = text("""SELECT paperID, name
        FROM Papers
        WHERE userID = :userID
        ORDER BY name""")
    return connection.execute(qry, userID=userID).fetchall()

def get_paper_filters(connection):
    """ Helper function to grab paper filters """
    qry = text("""SELECT paperFilterID, name FROM PaperFilters""")
    return connection.execute(qry).fetchall()

def get_paper_developers(connection):
    """ Helper function to grab paper developers """
    qry = text("""SELECT paperDeveloperID, CONCAT(name, ', 1:', dilution) AS
        name FROM PaperDevelopers""")
    return connection.execute(qry).fetchall()

def get_enlarger_lenses(connection):
    """ Helper function to get enlarger leneses """
    userID = current_user.get_id()
    qry = text("""SELECT enlargerLensID, name
        FROM EnlargerLenses
        WHERE userID = :userID""")
    return connection.execute(qry, userID=userID).fetchall()

def get_exposures(connection, filmID):
    """ Helper function to get exposures from a film """
    userID = current_user.get_id()
    qry = text("""SELECT exposureNumber AS exposureNumber,
        exposureNumber AS subject
        FROM Exposures
        WHERE userID = :userID
        AND filmID = :filmID""")

    result = connection.execute(qry,
                              userID=userID,
                              filmID=filmID).fetchall()
    list_result = []
    for row in result:
        item = (row[0], row[1])
        list_result.append(item)
    return list_result


def check_for_print_file(connection, printID):
    """ Check if a print has an associated image/file """
    userID = current_user.get_id()
    qry = text("""SELECT fileID FROM Prints
        WHERE printID = :printID AND userID = :userID""")
    result = connection.execute(qry,
                                printID=printID,
                                userID=userID).fetchone()
    if result:
        if result[0]:
            return int(result[0])
    return None

def get_paper_sizes():
    """ Helper function to return available paper sizes for the forms """
    return [('4x5', '4x5'),
            ('4x6', '4x6'),
            ('5x7', '5x7'),
            ('8x10', '8x10'),
            ('11x14', '11x14'),
            ('Other', 'Other')]

## Classes
# Forms
class TestForm(FlaskForm):
    """ Paper Tests Form """
    paperID = SelectField('Paper',
                          validators=[Optional()],
                          coerce=int)
    size = SelectField('Size',
                       validators=[DataRequired()],
                       choices=get_paper_sizes())
    enlargerLensID = SelectField('Enlarger Lens',
                                 validators=[Optional()],
                                 coerce=int)
    enlargerID = SelectField('Enlarger',
                             validators=[Optional()],
                             coerce=int)
    aperture = DecimalField('Aperture', places=1, validators=[Optional()])
    headHeight = IntegerField('Head Height',
                              validators=[NumberRange(min=0, max=255),
                                          Optional()])
    exposureTime = StringField('Exposure Time',
                               validators=[DataRequired(),
                                           functions.validate_exposure_time])
    notes = TextAreaField('Notes',
                          validators=[Optional()],
                          filters=[lambda x: x or None])

class PrintForm(FlaskForm):
    """ Form for prints """
    exposureNumber = SelectField('Exposure #',
                                 validators=[DataRequired()])
    paperID = SelectField('Paper',
                          validators=[Optional()],
                          coerce=int)
    paperDeveloperID = SelectField('Developer',
                                   validators=[Optional()],
                                   coerce=int)
    paperFilterID = SelectField('Filters',
                                validators=[Optional()],
                                coerce=int)
    printType = SelectField('Type',
                            validators=[DataRequired()],
                            choices=[('Enlargement', 'Enlargement'),
                                     ('Contact', 'Contact')])
    size = SelectField('Size',
                       validators=[DataRequired()],
                       choices=get_paper_sizes())
    enlargerLensID = SelectField('Enlarger Lens',
                                 validators=[Optional()],
                                 coerce=int)
    enlargerID = SelectField('Enlarger',
                             validators=[Optional()],
                             coerce=int)
    aperture = DecimalField('Aperture', places=1, validators=[Optional()])
    ndFilter = DecimalField('ND (Stops)',
                            places=1,
                            validators=[NumberRange(min=0, max=20),
                                        Optional()])
    headHeight = IntegerField('Head Height',
                              validators=[NumberRange(min=0, max=255),
                                          Optional()])
    exposureTime = StringField('Exposure Time',
                               validators=[DataRequired(),
                                           functions.validate_exposure_time])
    notes = TextAreaField('Notes',
                          validators=[Optional()],
                          filters=[lambda x: x or None])
    file = FileField('File (JPG)',
                     validators=[Optional(),
                                 FileAllowed(['jpg'], 'JPEGs Only')])

    def populate_select_fields(self, connection, filmID):
        """ Helper function to populate select drop downs """
        self.paperID.choices = optional_choices("None", get_papers(connection))
        self.paperDeveloperID.choices = optional_choices("None", get_paper_developers(connection))
        self.paperFilterID.choices = optional_choices("None", get_paper_filters(connection))
        self.enlargerLensID.choices = optional_choices("None", get_enlarger_lenses(connection))
        self.enlargerID.choices = optional_choices("None", get_enlargers(connection))
        self.exposureNumber.choices = get_exposures(connection, filmID)

class ContactSheetForm(FlaskForm):
    """ Form for contact sheets """
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
                            filters=[lambda x: x or None])
    headHeight = IntegerField('Head Height',
                              validators=[NumberRange(min=0, max=255),
                                          Optional()],
                              filters=[lambda x: x or None])
    exposureTime = StringField('Exposure Time',
                               validators=[DataRequired(),
                                           functions.validate_exposure_time])
    notes = TextAreaField('Notes',
                          validators=[Optional()],
                          filters=[lambda x: x or None])
    file = FileField('File (JPG)',
                     validators=[Optional(),
                                 FileAllowed(['jpg'], 'JPEGs Only')])

    def populate_select_fields(self, connection):
        """ Helper function to populate select fields """
        self.paperID.choices = optional_choices("None", get_papers(connection))
        self.paperFilterID.choices = optional_choices("None", get_paper_filters(connection))
        self.enlargerLensID.choices = optional_choices("None", get_enlarger_lenses(connection))
        self.enlargerID.choices = optional_choices("None", get_enlargers(connection))

### Darkroom Section
@app.route('/darkroom', methods=['GET'])
@login_required
def darkroom_index():
    """ Index page for darkroom section """
    return render_template('darkroom/index.html')

@app.route('/darkroom/tests', methods=['GET'])
@login_required
def user_tests():
    """ Manage user's paper tests """
    connection = engine.connect()
    transaction = connection.begin()
    userID = current_user.get_id()

    qry = text("""SELECT Papers.name AS paper,
        CONCAT(FilmTypes.name, ' ', FilmTypes.iso) AS film,
        Enlargers.name AS enlarger,
        EnlargerLenses.name AS lens,
        aperture, size, SEC_TO_TIME(exposureTime) AS exposureTime
        FROM MaxBlackTests
        JOIN Papers ON Papers.paperID = MaxBlackTests.paperID
            AND Papers.userID = MaxBlackTests.userID
        JOIN FilmTypes ON FilmTypes.filmTypeID = MaxBlackTests.filmTypeID
            AND FilmTypes.userID = MaxBlackTests.userID
        LEFT OUTER JOIN Enlargers ON Enlargers.userID = MaxBlackTests.userID
            AND Enlargers.enlargerID = MaxBlackTests.enlargerID
        LEFT OUTER JOIN EnlargerLenses ON EnlargerLenses.userID = MaxBlackTests.userID
            AND EnlargerLenses.enlargerLensID = MaxBlackTests.enlargerLensID
        WHERE MaxBlackTests.userID = :userID""")
    tests = connection.execute(qry, userID=userID)
    transaction.commit()
    return render_template('darkroom/tests.html', tests=tests)

### Darkroom Film Tabs
# pylint: disable=line-too-long
# This would seem less messy as one line over many.
@app.route('/binders/<int:binderID>/projects/<int:projectID>/films/<int:filmID>/prints', methods=['POST', 'GET'])
@login_required
def user_prints(binderID, projectID, filmID):
    """ Manage user's prints for a film """
    connection = engine.connect()
    transaction = connection.begin()
    userID = current_user.get_id()
    form = PrintForm()
    form.populate_select_fields(connection, filmID)

    if request.method == 'POST':
        if request.form['button'] == 'addPrint':
            if form.validate_on_submit():
                nextPrintID = functions.next_id(connection, 'printID', 'Prints')
                log("Next Print ID: %s" % nextPrintID)
                # If user included a file, let's upload it. Otherwise skip it.
                if form.file.data:
                    nextFileID = functions.next_id(connection, 'fileID', 'Files')
                    files.upload_file(request, connection, transaction, nextFileID)
                else:
                    nextFileID = None

                qry = text("""INSERT INTO Prints
                    (printID, paperDeveloperID, filmID, exposureNumber, userID, paperID, paperFilterID,
                    enlargerLensID, enlargerID, fileID, aperture, ndFilter, headHeight, exposureTime, printType, size, notes)
                    VALUES (:printID, :paperDeveloperID, :filmID, :exposureNumber, :userID, :paperID,
                    :paperFilterID, :enlargerLensID, :enlargerID, :fileID, :aperture, :ndFilter, :headHeight, :exposureTime,
                    :printType, :size, :notes)""")
                insert(connection, qry, "Print",
                       printID=nextPrintID,
                       filmID=filmID,
                       userID=userID,
                       fileID=nextFileID,
                       paperDeveloperID=zero_to_none(form.paperDeveloperID.data),
                       exposureNumber=form.exposureNumber.data,
                       paperID=zero_to_none(form.paperID.data),
                       paperFilterID=zero_to_none(form.paperFilterID.data),
                       enlargerLensID=zero_to_none(form.enlargerLensID.data),
                       enlargerID=zero_to_none(form.enlargerID.data),
                       aperture=form.aperture.data,
                       ndFilter=form.ndFilter.data,
                       headHeight=form.headHeight.data,
                       exposureTime=functions.time_to_seconds(form.exposureTime.data),
                       printType=form.printType.data,
                       size=form.size.data,
                       notes=form.notes.data)
    film = functions.get_film_details(connection, binderID, projectID, filmID)

    qry = text("""SELECT printID, exposureNumber,
        PaperDevelopers.name AS paperDeveloperName,
        PaperDevelopers.dilution AS paperDeveloperDilution,
        Papers.name AS paperName,
        PaperFilters.name AS paperFilterName,
        printType, size, aperture, ndFilter, headHeight, Prints.notes, fileID,
        EnlargerLenses.name AS lens,
        Enlargers.name AS enlarger,
        SECONDS_TO_DURATION(exposureTime) AS exposureTime
        FROM Prints
        LEFT OUTER JOIN Papers ON Papers.paperID = Prints.paperID
            AND Papers.userID = Prints.userID
        LEFT OUTER JOIN PaperFilters ON PaperFilters.paperFilterID = Prints.paperFilterID
        LEFT OUTER JOIN PaperDevelopers ON PaperDevelopers.paperDeveloperID = Prints.paperDeveloperID
        LEFT OUTER JOIN EnlargerLenses ON EnlargerLenses.enlargerLensID = Prints.enlargerLensID
            AND EnlargerLenses.userID = Prints.userID
        LEFT OUTER JOIN Enlargers ON Enlargers.enlargerID = Prints.enlargerID
            AND Enlargers.userID = Prints.userID
        WHERE filmID = :filmID AND Prints.userID = :userID""")
    prints = connection.execute(qry,
                                userID=userID,
                                filmID=filmID)

    transaction.commit()
    return render_template('darkroom/prints.html',
                           form=form,
                           binderID=binderID,
                           projectID=projectID,
                           film=film,
                           prints=prints,
                           view='prints')

# pylint: disable=line-too-long
# This would seem less messy as one line over many.
@app.route('/binders/<int:binderID>/projects/<int:projectID>/films/<int:filmID>/prints/<int:printID>', methods=['POST', 'GET'])
@login_required
def print_exposure(binderID, projectID, filmID, printID):
    """ Manage a specific exposure print """
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
                               printID=printID,
                               userID=userID)
            if fileID:
                files.delete_file(connection, transaction, fileID)
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
                        files.delete_file(connection, transaction, fileID)
                        files.upload_file(request, connection, transaction, fileID)
                    else:
                        app.logger.info('Brand New File')
                        fileID = functions.next_id(connection, 'fileID', 'Files')
                        files.upload_file(request, connection, transaction, fileID)
                qry = text("""REPLACE INTO Prints
                    (printID, filmID, exposureNumber, userID, paperID, paperFilterID,
                    enlargerLensID, enlargerID, fileID, aperture, ndFilter, headHeight, exposureTime, printType, size, notes)
                    VALUES (:printID, :filmID, :exposureNumber, :userID, :paperID,
                    :paperFilterID, :enlargerLensID, :enlargerID, :fileID, :aperture, :ndFilter, :headHeight, :exposureTime,
                    :printType, :size, :notes)""")
                insert(connection, qry, "Print",
                       printID=printID,
                       filmID=filmID,
                       userID=userID,
                       fileID=fileID,
                       exposureNumber=form.exposureNumber.data,
                       paperID=zero_to_none(form.paperID.data),
                       paperFilterID=zero_to_none(form.paperFilterID.data),
                       enlargerLensID=zero_to_none(form.enlargerLensID.data),
                       enlargerID=zero_to_none(form.enlargerID.data),
                       aperture=form.aperture.data,
                       ndFilter=form.ndFilter.data,
                       headHeight=form.headHeight.data,
                       exposureTime=functions.time_to_seconds(form.exposureTime.data),
                       #exposureTime=form.exposureTime.data,
                       printType=form.printType.data,
                       size=form.size.data,
                       notes=form.notes.data)
                transaction.commit()
                return redirect('/binders/' + str(binderID)
                                + '/projects/' + str(projectID)
                                + '/films/' + str(filmID)
                                + '/prints')

    film = functions.get_film_details(connection, binderID, projectID, filmID)
    qry = text("""SELECT printID, exposureNumber, Papers.name AS paperName,
        PaperDevelopers.name AS paperDeveloperName,
        PaperDevelopers.dilution AS paperDeveloperDilution,
        Papers.paperID, PaperFilters.paperFilterID, PaperFilters.name AS paperFilterName,
        EnlargerLenses.enlargerLensID, EnlargerLenses.name AS enlargerLensName,
        Enlargers.enlargerID, Enlargers.name AS enlargerName,
        printType, size, aperture, ndFilter, headHeight, Prints.notes, fileID,
        SECONDS_TO_DURATION(exposureTime) AS exposureTime
        FROM Prints
        LEFT OUTER JOIN Papers ON Papers.paperID = Prints.paperID
            AND Papers.userID = Prints.userID
        LEFT OUTER JOIN PaperDevelopers ON PaperDevelopers.paperDeveloperID = Prints.paperDeveloperID
        LEFT OUTER JOIN PaperFilters ON PaperFilters.paperFilterID = Prints.paperFilterID
        LEFT OUTER JOIN EnlargerLenses ON EnlargerLenses.enlargerLensID = Prints.enlargerLensID
            AND EnlargerLenses.userID = Prints.userID
        LEFT OUTER JOIN Enlargers ON Enlargers.enlargerID = Prints.enlargerID
            AND Enlargers.userID = Prints.userID
        WHERE Prints.userID = :userID
        AND Prints.printID = :printID""")
    print_details = connection.execute(qry,
                                       userID=userID,
                                       printID=printID).fetchone()
    transaction.commit()
    form = PrintForm(data=print_details)
    form.populate_select_fields(connection, filmID)
    return render_template('darkroom/print.html',
                           form=form,
                           film=film,
                           binderID=binderID,
                           projectID=projectID,
                           printID=printID,
                           print_details=print_details,
                           view='prints')

# pylint: disable=line-too-long
# This would seem less messy as one line over many.
@app.route('/binders/<int:binderID>/projects/<int:projectID>/films/<int:filmID>/contactsheet', methods=['POST', 'GET'])
@login_required
def contactsheet(binderID, projectID, filmID):
    """ Manage a contact sheet """
    connection = engine.connect()
    transaction = connection.begin()
    userID = current_user.get_id()
    form = ContactSheetForm()
    form.populate_select_fields(connection)

    # Upload a new contact sheet
    if request.method == 'POST':
        nextFileID = None
        # See if there is a contact sheet already
        qry = text("""SELECT fileID FROM ContactSheets
            WHERE filmID = :filmID AND userID = :userID""")
        result = connection.execute(qry,
                                    filmID=filmID,
                                    userID=userID).fetchone()
        if result:
            if result[0]:
                fileID = int(result[0])
            else:
                fileID = None
        else:
            fileID = None
        if request.form['button'] == 'deleteCS':
            qry = text("""DELETE FROM ContactSheets
                WHERE filmID = :filmID AND userID = :userID""")
            connection.execute(qry,
                               filmID=filmID,
                               userID=userID)
            if fileID:
                files.delete_file(connection, transaction, fileID)
        elif request.form['button'] == 'updateCS' and form.validate_on_submit():
            # If user included a file, let's upload it. Otherwise skip it.
            if 'file' in request.files:
                file_upload = request.files['file']
                if file_upload.filename != '':
                    nextFileID = functions.next_id(connection, 'fileID', 'Files')
                    files.upload_file(request, connection, transaction, nextFileID)
            # If we're updating an existing sheet and the user didn't upload
            # a new file, use the old one.
            else:
                nextFileID = fileID
            qry = text("""REPLACE INTO ContactSheets (filmID, userID, fileID, paperID, paperFilterID, enlargerLensID, enlargerID, aperture, headHeight, exposureTime, notes)
                VALUES (:filmID, :userID, :fileID, :paperID, :paperFilterID, :enlargerLensID, :enlargerID, :aperture, :headHeight, :exposureTime, :notes)""")
            connection.execute(qry,
                               filmID=filmID,
                               userID=userID,
                               fileID=nextFileID,
                               paperID=zero_to_none(form.paperID.data),
                               paperFilterID=zero_to_none(form.paperFilterID.data),
                               enlargerLensID=zero_to_none(form.enlargerLensID.data),
                               enlargerID=zero_to_none(form.enlargerID.data),
                               aperture=form.aperture.data,
                               headHeight=form.headHeight.data,
                               exposureTime=functions.time_to_seconds(form.exposureTime.data),
                               notes=form.notes.data)
    film = functions.get_film_details(connection, binderID, projectID, filmID)

    # Get contact sheet info
    qry = text("""SELECT fileID, Papers.name AS paperName,
        PaperFilters.name AS paperFilterName,
        EnlargerLenses.name AS lens, Enlargers.name AS enlarger,
        aperture, headHeight, ContactSheets.notes,
        ContactSheets.paperID AS paperID,
        ContactSheets.paperFilterID AS paperFilterID,
        ContactSheets.enlargerLensID AS enlargerLensID,
        SECONDS_TO_DURATION(exposureTime) AS exposureTime
        FROM ContactSheets
        LEFT OUTER JOIN Papers ON Papers.paperID = ContactSheets.paperID
            AND Papers.userID = ContactSheets.userID
        LEFT OUTER JOIN PaperFilters ON PaperFilters.paperFilterID = ContactSheets.paperFilterID
        LEFT OUTER JOIN EnlargerLenses ON EnlargerLenses.enlargerLensID = ContactSheets.enlargerLensID
            AND EnlargerLenses.userID = ContactSheets.userID
        LEFT OUTER JOIN Enlargers ON Enlargers.enlargerID = ContactSheets.enlargerID
            AND Enlargers.userID = ContactSheets.userID
        WHERE filmID = :filmID AND ContactSheets.userID = :userID""")
    contactSheet = connection.execute(qry,
                                      userID=userID,
                                      binderID=binderID,
                                      filmID=filmID).fetchone()
    if contactSheet:
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
