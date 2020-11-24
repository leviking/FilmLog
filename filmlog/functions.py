""" A set of usable generic helper functions """
from flask import flash
from flask_login import current_user
from sqlalchemy.sql import text
from sqlalchemy.exc import IntegrityError
from wtforms.validators import ValidationError
from filmlog import abort
from filmlog.config import app

# Functions
def result_to_dict(result_set):
    """ Return a dictionary from a DB result set """
    return [dict(row) for row in result_set]

def next_id(connection, field, table):
    """
        Grab the next id based on the max ID of the provided table and field.
        Be careful as this could allow for sql-injection!
    """
    qry = text("""SELECT MAX(""" + field + """) AS currentID FROM """ + table + \
               """ WHERE userID = :userID""")
    result = connection.execute(qry,
                                userID=int(current_user.get_id())).fetchone()
    app.logger.info('Current ID: %s', result.currentID)
    if result.currentID is not None:
        return int(result.currentID) + 1
    return 1

def get_film_types(connection):
    """ Get a friendly output of the film types (e.g. Kodak T-Max 100) """
    userID = current_user.get_id()
    qry = text("""SELECT filmTypeID,
        CONCAT(name, " ", iso) AS name
        FROM FilmTypes
        WHERE userID = :userID
        ORDER BY name""")
    # All this is stupid. The original return used to work but now it doesn't.
    result = connection.execute(qry, userID=userID).fetchall()
    list_result = []
    for row in result:
        item = (row[0], row[1])
        list_result.append(item)
    return list_result
    # Used to work now broke
    #return connection.execute(qry, userID=userID).fetchall()

def get_film_sizes(connection):
    """ Get all the available film sizes (e.g. 35mm, 4x5) """
    qry = text("""SELECT filmSizeID, size
        FROM FilmSizes""")
    # All this is stupid. The original return used to work but now it doesn't.
    result = connection.execute(qry).fetchall()
    list_result = []
    for row in result:
        item = (row[0], row[1])
        list_result.append(item)
    return list_result
    # Used to work now broke
    #return connection.execute(qry).fetchall()

def get_film_details(connection, binderID, projectID, filmID):
    """ Get detailed informatiln of a particular film shot.
        For sheets, each "film" is more of a sub project. """
    userID = current_user.get_id()

    qry = text("""SELECT filmID, Films.projectID, Projects.name AS project,
        FilmTypes.name AS filmName, FilmTypes.iso AS filmISO,
        Films.iso AS shotISO, fileNo, fileDate, FilmSizes.size AS size,
        Films.filmSizeID AS filmSizeID,
        FilmSizes.type AS filmSizeType,
        FilmSizes.format AS filmSizeFormat,
        title,
        FilmTypes.filmTypeID AS filmTypeID, loaded, unloaded, developed, development,
        Cameras.name AS camera,
        Cameras.cameraID AS cameraID, Films.notes
        FROM Films
        JOIN Projects ON Projects.projectID = Films.projectID
            AND Projects.userID = Films.userID
        JOIN Binders ON Binders.binderID = Projects.binderID
            AND  Binders.userID = Films.userID
        LEFT OUTER JOIN FilmTypes ON FilmTypes.filmTypeID = Films.filmTypeID
            AND FilmTypes.userID = Films.userID
        JOIN FilmSizes ON FilmSizes.filmSizeID = Films.filmSizeID
        LEFT JOIN Cameras ON Cameras.cameraID = Films.cameraID
            AND Cameras.userID = Films.userID
        WHERE Films.projectID = :projectID
        AND filmID = :filmID
        AND Projects.binderID = :binderID
        AND Binders.userID = :userID""")

    film = connection.execute(qry,
                              userID=userID,
                              binderID=binderID,
                              projectID=projectID,
                              filmID=filmID).fetchone()

    if not film:
        abort(404)

    return film

def get_enlargers(connection):
    """ Helper function to get enlargers """
    userID = current_user.get_id()
    qry = text("""SELECT enlargerID, name
        FROM Enlargers
        WHERE userID = :userID""")
    return connection.execute(qry, userID=userID).fetchall()

def optional_choices(name, choices):
    """ Helper function to append extra choices to a form.
        This is typically used to inject "None" as a choice. """
    new_choices = [(0, name)]
    for row in choices:
        new_choices.append(row)
    return new_choices

def zero_to_none(value):
    """ Helper function to set 0 or '0' (the string) to None or null. """
    if value in (0, '0'):
        return None
    return value

def insert(connection, qry, item, **args):
    """ Helper function to make insert checks easier and more consistent.
        An error causes an implicit rollback. """
    try:
        connection.execute(qry, args)
    except IntegrityError:
        flash(item + " of the same name already exists.")

def delete(connection, qry, item, **args):
    """ Attempt a delete (or really any query) and catch the error.
        Delete exceptions will typically be if there are any foreign key
        relationships that do not have cascading deletes. """
    try:
        connection.execute(qry, args)
    except IntegrityError:
        flash("Cannot delete " + item +
              ". Could be you may have stuff that depends on it.")

def time_to_seconds(time):
    """ If time is in MM:SS format, calculate the raw seconds.
        Otherwise just return the time as-is. """
    if time:
        if ':' not in time:
            if int(time) > 0:
                return int(time)
        else:
            m, s = time.split(':')
            return int(m) * 60 + int(s)
    raise ValidationError('Time in wrong format, it should be MM:SS.')

def validate_exposure_time(form, field):
    """ Make sure the provided exposure time is in a convertable format. """
    # pylint: disable=unused-argument
    # Disabling unused argument due to
    # https://wtforms.readthedocs.io/en/stable/validators.html
    try:
        time_to_seconds(field.data)
    except Exception:
        raise ValidationError('Time in wrong format, should be MM:SS.') from None

# Unused (see SECONDS_TO_DURATION MySQL function instead)
#def seconds_to_time(seconds):
#    return str(int(seconds / 60)) + ":" + str(int(seconds % 60))
