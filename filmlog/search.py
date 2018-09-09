from flask import request, render_template, redirect, url_for, abort
from sqlalchemy.sql import select, text, func
import os, re

from flask_login import LoginManager, login_required, current_user

from filmlog import app
from filmlog import database, engine

@app.route('/search',  methods = ['GET'])
@login_required
def search():
    connection = engine.connect()
    transaction = connection.begin()
    userID = current_user.get_id()
    search = request.args.get('search')

    qry = text("""SELECT Projects.binderID, Projects.projectID,
        Projects.name AS project_name, Binders.name AS binder_name,
        filmCount, Projects.createdOn
        FROM Projects
        JOIN Binders ON Binders.binderID = Projects.binderID
        WHERE Projects.userID = :userID
        AND Projects.name LIKE ('%""" + search + """%')
        ORDER BY createdOn""")
    projects = connection.execute(qry,
        userID = userID,
        search = search).fetchall()

    qry = text("""SELECT filmID, Films.projectID, binderID,
        title, fileNo, fileDate,
        Films.iso AS iso, brand, FilmTypes.name AS filmName,
        FilmSizes.size AS size, exposures,
        Cameras.name AS camera
        FROM Films
        JOIN Projects ON Projects.projectID = Films.projectID
        LEFT OUTER JOIN FilmTypes ON FilmTypes.filmTypeID = Films.filmTypeID
        LEFT OUTER JOIN FilmBrands ON FilmBrands.filmBrandID = FilmTypes.filmBrandID
        JOIN FilmSizes ON FilmSizes.filmSizeID = Films.filmSizeID
        JOIN Cameras ON Cameras.cameraID = Films.cameraID
        WHERE Films.userID = :userID
        AND (Films.title LIKE ('%""" + search + """%')
        OR Films.notes LIKE ('%""" + search + """%'))
        ORDER BY fileDate""")
    films = connection.execute(qry, userID=userID).fetchall()


    transaction.commit()
    return render_template('search.html',
        search = search,
        projects = projects,
        films = films)
