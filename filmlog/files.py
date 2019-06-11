""" File management """
import os
from shutil import rmtree

from flask import send_from_directory, flash, abort
from flask_login import login_required, current_user
from sqlalchemy.sql import text
from PIL import Image
# from werkzeug.utils import secure_filename

from filmlog.config import app

def is_file_allowed(filename):
    """ Is the file allowed """
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

def delete_file(connection, transaction, fileID):
    """ Delete a file from the filesystem and the database """
    app.logger.info('Delete file')
    userID = current_user.get_id()
    try:
        filepath = os.path.join(app.config['UPLOAD_FOLDER'],
                                str(userID),
                                str(fileID))
        app.logger.debug('filepath, %s', filepath)
        os.path.isfile(filepath)
        rmtree(filepath)
    # pylint: disable=broad-except
    # This could be improved but needs time and work and, as it stands
    # this does work.
    except Exception:
        app.logger.debug('Exception and Rollback')
        transaction.rollback()
        abort(400)
    app.logger.debug('Remove file from database')
    qry = text("""DELETE FROM Files WHERE userID=:userID AND fileID=:fileID""")
    connection.execute(qry,
                       fileID=fileID,
                       userID=userID)
    return True

def upload_file(request, connection, transaction, fileID):
    """ Upload a file to the database and filesystem """
    app.logger.info('Upload file')
    userID = current_user.get_id()
    if 'file' not in request.files:
        flash('File missing')
    file_upload = request.files['file']
    if file_upload.filename == '':
        flash('File missing')
    if file_upload and is_file_allowed(file_upload.filename):
        # We rename the file so this may not be required
        # filename = secure_filename(file.filename)
        try:
            directory = os.path.join(app.config['UPLOAD_FOLDER'],
                                     str(userID),
                                     str(fileID))
            if not os.path.exists(directory):
                os.makedirs(directory)
            file_upload.save(os.path.join(directory + "/full.jpg"))
            generate_thumbnail(fileID)
            qry = text("""INSERT INTO Files (fileID, userID)
                VALUES (:fileID, :userID)""")
            connection.execute(qry,
                               fileID=fileID,
                               userID=userID)
            app.logger.debug('Upload Finished')

        # pylint: disable=broad-except
        # This could be improved but needs time and work and, as it stands
        # this does work.
        except Exception:
            app.logger.debug('Exception and Rollback')
            transaction.rollback()
            abort(400)
    return True

def generate_thumbnail(fileID):
    """ Generate and store a thumbnail image """
    userID = current_user.get_id()
    fullsize = os.path.join(app.config['UPLOAD_FOLDER'], str(userID), str(fileID), "full.jpg")
    size = int(app.config['THUMBNAIL_SIZE']), int(app.config['THUMBNAIL_SIZE'])
    image = Image.open(fullsize)
    image.thumbnail(size, Image.ANTIALIAS)
    image.save(os.path.join(app.config['UPLOAD_FOLDER'], str(userID), str(fileID), "thumb.jpg"))

@app.route('/files/thumb/<int:fileID>')
@login_required
def get_thumbnail(fileID):
    """ Get the thumbnail of an image """
    userID = current_user.get_id()
    return send_from_directory(
        app.config['UPLOAD_FOLDER'],
        str(userID) + "/" + str(fileID) + "/thumb.jpg")

@app.route('/files/full/<int:fileID>')
@login_required
def get_fullsize(fileID):
    """ Get the fullsize image """
    userID = current_user.get_id()
    return send_from_directory(
        app.config['UPLOAD_FOLDER'],
        str(userID) + "/" + str(fileID) + "/full.jpg")
