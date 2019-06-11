""" Search section (/search) """
import re
from flask import request, render_template
from flask_login import login_required, current_user
from sqlalchemy.sql import text

from filmlog.config import app, engine

@app.route('/search', methods=['GET'])
@login_required
def search_index():
    """ Index page for search section """
    connection = engine.connect()
    transaction = connection.begin()
    userID = current_user.get_id()
    search = re.escape(request.args.get('search'))

    qry = text("""SELECT Projects.binderID, Projects.projectID,
        Projects.name AS project_name, Binders.name AS binder_name,
        filmCount, Projects.createdOn
        FROM Projects
        JOIN Binders ON Binders.binderID = Projects.binderID
            AND Binders.userID = Projects.userID
        WHERE Projects.userID = :userID
        AND Projects.name LIKE ('%""" + search + """%')
        ORDER BY createdOn""")
    projects = connection.execute(qry, userID=userID, search=search).fetchall()

    qry = text("""SELECT filmID, Films.projectID, binderID,
        title, fileNo, fileDate,
        Films.iso AS iso, brand, FilmTypes.name AS filmName,
        FilmSizes.size AS size, exposures,
        Cameras.name AS camera
        FROM Films
        JOIN Projects ON Projects.projectID = Films.projectID
            AND Projects.userID = Films.userID
        LEFT OUTER JOIN FilmTypes ON FilmTypes.filmTypeID = Films.filmTypeID
        LEFT OUTER JOIN FilmBrands ON FilmBrands.filmBrandID = FilmTypes.filmBrandID
        JOIN FilmSizes ON FilmSizes.filmSizeID = Films.filmSizeID
        JOIN Cameras ON Cameras.cameraID = Films.cameraID
            AND Cameras.userID = Films.userID
        WHERE Films.userID = :userID
        AND (Films.title LIKE ('%""" + search + """%')
        OR Films.notes LIKE ('%""" + search + """%'))
        ORDER BY fileDate""")
    films = connection.execute(qry, userID=userID).fetchall()

    qry = text("""SELECT Films.title AS film_title, Exposures.filmID,
        Films.projectID, Projects.binderID,
        exposureNumber, shutter, aperture,
        Exposures.subject, Exposures.notes
        FROM Exposures
        JOIN Films ON Films.filmID = Exposures.filmID
        JOIN Projects ON Projects.projectID = Films.projectID
            AND Projects.userID = Films.userID
        WHERE Exposures.userID = :userID
        AND (Exposures.subject LIKE ('%""" + search + """%')
        OR Exposures.notes LIKE ('%""" + search + """%'))
        ORDER BY Films.filmID, exposureNumber""")
    exposures = connection.execute(qry, userID=userID).fetchall()

    transaction.commit()
    return render_template('search.html',
                           search=search,
                           projects=projects,
                           films=films,
                           exposures=exposures)
