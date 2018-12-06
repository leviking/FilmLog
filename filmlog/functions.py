from filmlog import app, abort
from flask import flash
from sqlalchemy.sql import text
from flask_login import current_user
from sqlalchemy.exc import IntegrityError


# Functions
def result_to_dict(result_set):
    return [dict(row) for row in result_set]

# This allows for SQL injection if yuo're not careful!
def next_id(connection, field, table):
    qry = text("""SELECT MAX(""" + field + """) AS currentID FROM """ + table + """ WHERE userID = :userID""")
    result = connection.execute(qry,
        userID = int(current_user.get_id())).fetchone()
    app.logger.info('Current ID: %s', result.currentID)
    if result.currentID is not None:
        return int(result.currentID) + 1
    else:
        return 1

def get_film_types(connection):
    qry = text("""SELECT filmTypeID,
        CONCAT(brand, " ", name, " ", iso)
        FROM FilmTypes
        JOIN FilmBrands ON FilmBrands.filmBrandID = FilmTypes.filmBrandID
        ORDER BY brand, name""")
    return connection.execute(qry).fetchall()

def get_film_sizes(connection):
    qry = text("""SELECT filmSizeID, size
        FROM FilmSizes""")
    return connection.execute(qry).fetchall()

def get_film_details(connection, binderID, projectID, filmID):
    userID = current_user.get_id()

    qry = text("""SELECT filmID, Films.projectID, Projects.name AS project, brand,
        FilmTypes.name AS filmName, FilmTypes.iso AS filmISO,
        Films.iso AS shotISO, fileNo, fileDate, FilmSizes.size AS size,
        Films.filmSizeID AS filmSizeID,
        FilmSizes.type AS filmSizeType,
        FilmSizes.format AS filmSizeFormat,
        title,
        FilmTypes.filmTypeID AS filmTypeID, loaded, unloaded, developed, development,
        Cameras.name AS camera,
        Cameras.cameraID AS cameraID, notes
        FROM Films
        JOIN Projects ON Projects.projectID = Films.projectID
            AND Projects.userID = Films.userID
        JOIN Binders ON Binders.binderID = Projects.binderID
            AND  Binders.userID = Films.userID
        LEFT OUTER JOIN FilmTypes ON FilmTypes.filmTypeID = Films.filmTypeID
        LEFT OUTER JOIN FilmBrands ON FilmBrands.filmBrandID = FilmTypes.filmBrandID
        JOIN FilmSizes ON FilmSizes.filmSizeID = Films.filmSizeID
        LEFT JOIN Cameras ON Cameras.cameraID = Films.cameraID
            AND Cameras.userID = Films.userID
        WHERE Films.projectID = :projectID
        AND filmID = :filmID
        AND Projects.binderID = :binderID
        AND Binders.userID = :userID""")

    film = connection.execute(qry,
        userID = userID,
        binderID = binderID,
        projectID=projectID,
        filmID=filmID).fetchone()

    if not film:
        abort(404)

    return film

def optional_choices(name, choices):
    new_choices = [(0, name)]
    for row in choices:
        new_choices.append(row)
    return new_choices

def zero_to_none(value):
    if value == 0 or value == '0':
        return None
    return value

# Try an insert (really could be any query),
# catch the error and provide info.
# An error causes an implicit rollback.
def insert(connection, qry, item, **args):
    try:
         connection.execute(qry, args)
    except IntegrityError:
        flash(item + " of the same name already exists.")

# Attempt a delete (or really any query),
# catch the error and provide info.
# An error causes an implicty rollback.
# Delete exceptions will typically be if there
# are foreign key relationships that do not
# have cascading deletes.
def delete(connection, qry, item, **args):
    try:
         connection.execute(qry, args)
    except IntegrityError:
        flash("Cannot delete " + item +
            ". Could be you may have stuff that depends on it.")

# Unused (see SECONDS_TO_DURATION MySQL function instead)
#def seconds_to_time(seconds):
#    return str(int(seconds / 60)) + ":" + str(int(seconds % 60))
