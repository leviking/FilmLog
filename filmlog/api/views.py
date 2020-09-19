""" Main view for FilmLog application, where all other views come in """
from flask_login import login_required
from flask import request

# Filmlog
from filmlog.api import api_blueprint, binders, projects, filmstock, holders, \
                        films, cameras, user, paper
from filmlog.config import engine

# http://jsonapi.org/format/

@api_blueprint.route('/', methods=['GET'])
def index():
    """ Index page for API """
    return "Hello"

# General Public Endpoints
@api_blueprint.route('/filmsizes', methods=['GET'])
@login_required
def film_sizes():
    """ Get global film size information """
    connection = engine.connect()
    transaction = connection.begin()

    if request.method == 'GET':
        return_status = films.get_film_sizes(connection)
    transaction.commit()
    return return_status

# Cameras
@api_blueprint.route('/cameras', methods=['GET'])
@login_required
def cameras_active():
    """ Get cameras information """
    connection = engine.connect()
    transaction = connection.begin()

    if request.method == 'GET':
        return_status = cameras.get_all(connection)
    transaction.commit()
    return return_status

@api_blueprint.route('/cameras/<int:cameraID>',
                     methods=['GET', 'PATCH'])
@login_required
def camera(cameraID):
    """ Get camera """
    connection = engine.connect()
    transaction = connection.begin()
    if request.method == 'GET':
        return_status = cameras.get(connection, cameraID)
    if request.method == 'PATCH':
        return_status = cameras.patch(connection, cameraID)
    transaction.commit()
    return return_status

@api_blueprint.route('/cameras/<int:cameraID>/loadFilm/<int:filmTypeID>',
                     methods=['PATCH'])
@login_required
def load_camera(cameraID, filmTypeID):
    """ Get camera """
    connection = engine.connect()
    transaction = connection.begin()
    if request.method == 'PATCH':
        return_status = cameras.loadFilm(connection, cameraID, filmTypeID)
    transaction.commit()
    return return_status

# Films
@api_blueprint.route('/films', methods=['GET', 'POST'])
@login_required
def films_list():
    """ Get user's film types """
    connection = engine.connect()
    transaction = connection.begin()

    if request.method == 'GET':
        return_status = films.get_film_types(connection)
    elif request.method == 'POST':
        return_status = films.add_film_type(connection)
    transaction.commit()
    return return_status

@api_blueprint.route('/films/<int:filmTypeID>',
                     methods=['DELETE'])
@login_required
def film_type_details(filmTypeID):
    """ Get film type details """
    connection = engine.connect()
    transaction = connection.begin()
    if request.method == 'DELETE':
        return_status = films.delete_film_type(connection, filmTypeID)
    transaction.commit()
    return return_status

@api_blueprint.route('/film/<int:filmTypeID>/tests',
                      methods=['GET'])
@login_required
def film_tests(filmTypeID):
    """ Get user's film types """
    connection = engine.connect()
    transaction = connection.begin()
    if request.method == 'GET':
        return_status = films.get_film_tests(connection, filmTypeID)
    transaction.commit()
    return return_status

# Binders
@api_blueprint.route('/binders', methods=['GET', 'POST'])
@login_required
def binders_all():
    """ Get all binders """
    connection = engine.connect()
    transaction = connection.begin()
    if request.method == 'GET':
        return_status = binders.get_all(connection)
    elif request.method == 'POST':
        return_status = binders.post(connection)
    transaction.commit()
    return return_status

@api_blueprint.route('/binders/<int:binderID>',
                     methods=['GET', 'PATCH', 'DELETE'])
@login_required
def binder_details(binderID):
    """ Get binder details """
    connection = engine.connect()
    transaction = connection.begin()
    if request.method == 'GET':
        return_status = binders.get(connection, binderID)
    elif request.method == 'PATCH':
        return_status = binders.patch(connection, binderID)
    elif request.method == 'DELETE':
        return_status = binders.delete(connection, binderID)
    transaction.commit()
    return return_status

@api_blueprint.route('/binders/<int:binderID>/projects', methods=['GET', 'POST'])
@login_required
def projects_all(binderID):
    """ Get all projects under a binder """
    connection = engine.connect()
    transaction = connection.begin()

    if request.method == 'GET':
        return_status = projects.get_all(connection, binderID)
    elif request.method == 'POST':
        return_status = projects.post(connection, binderID)
    transaction.commit()
    return return_status

@api_blueprint.route('/binders/<int:binderID>/projects/<int:projectID>',
                     methods=['GET', 'DELETE'])
@login_required
def project_details(binderID, projectID):
    """ Get details of a project """
    connection = engine.connect()
    transaction = connection.begin()

    if request.method == 'GET':
        return_status = projects.get(connection, binderID, projectID)
    elif request.method == 'DELETE':
        return_status = projects.delete(connection, binderID, projectID)
    transaction.commit()
    return return_status

## Films
@api_blueprint.route('/binders/<int:binderID>/projects/<int:projectID>/films',
                     methods=['GET', 'POST'])
@login_required
def films_all(binderID, projectID):
    """ Get details of a project """
    connection = engine.connect()
    transaction = connection.begin()
    if request.method == 'GET':
        return_status = films.get_all(connection, binderID, projectID)
    if request.method == 'POST':
        return_status = films.post(connection, projectID)
    transaction.commit()
    return return_status

@api_blueprint.route('/binders/<int:binderID>/projects/<int:projectID>/films/<int:filmID>',
                     methods=['GET', 'DELETE'])
@login_required
def film_details(binderID, projectID, filmID):
    """ Get details of a film """
    connection = engine.connect()
    transaction = connection.begin()
    if request.method == 'GET':
        return_status = films.get(connection, binderID, projectID, filmID)
    if request.method == 'DELETE':
        return_status = films.delete(connection, filmID)
    transaction.commit()
    return return_status

@api_blueprint.route('/filmstock', methods=['GET'])
@login_required
def filmstock_all():
    """ Get available filmstocks """
    connection = engine.connect()
    transaction = connection.begin()

    if request.method == 'GET':
        return_status = filmstock.get_all(connection)
    transaction.commit()
    return return_status

@api_blueprint.route('/filmstock/<int:filmTypeID>:<int:filmSizeID>',
                     methods=['GET', 'PATCH', 'DELETE'])
@login_required
def filmstock_details(filmTypeID, filmSizeID):
    """ Get detailed filmstock information """
    connection = engine.connect()
    transaction = connection.begin()

    if request.method == 'GET':
        return_status = filmstock.get(connection, filmTypeID, filmSizeID)
    if request.method == 'PATCH':
        return_status = filmstock.patch(connection, filmTypeID, filmSizeID)
    if request.method == 'DELETE':
        return_status = filmstock.delete(connection, filmTypeID, filmSizeID)
    transaction.commit()
    return return_status

## Holders
@api_blueprint.route('/holders', methods=['GET', 'POST'])
@login_required
def holders_all():
    """ Get all user's holders filmstock information """
    connection = engine.connect()
    transaction = connection.begin()

    if request.method == 'GET':
        return_status = holders.get_all(connection)
    if request.method == 'POST':
        return_status = holders.post(connection)
    transaction.commit()
    return return_status

@api_blueprint.route('/holders/<string:status>', methods=['GET'])
@login_required
def holders_all_status(status):
    """ Get all user's holders filmstock information """
    connection = engine.connect()
    transaction = connection.begin()

    if request.method == 'GET':
        return_status = holders.get_all(connection, status)
    transaction.commit()
    return return_status

@api_blueprint.route('/holders/<int:holderID>', methods=['GET', 'PATCH'])
@login_required
def holder_details(holderID):
    """ Get detailed holder information """
    connection = engine.connect()
    transaction = connection.begin()
    #if request.method == 'GET':
    #    return_status = filmstock.get(connection, filmTypeID, filmSizeID)
    if request.method == 'PATCH':
        return_status = holders.patch(connection, holderID)
    transaction.commit()
    return return_status

@api_blueprint.route('/papers', methods=['GET', 'POST'])
@login_required
def papers_all():
    """ Get User's Papers """
    connection = engine.connect()
    transaction = connection.begin()
    if request.method == 'GET':
        return_status = paper.get_all(connection)
    if request.method == 'POST':
        return_status = paper.post(connection)
    transaction.commit()
    return return_status

@api_blueprint.route('/papers/<int:paperID>', methods=['DELETE'])
@login_required
def papers_delete(paperID):
    """ Delete Paper """
    connection = engine.connect()
    transaction = connection.begin()
    return_status = paper.delete(connection, paperID)
    transaction.commit()
    return return_status

@api_blueprint.route('/user/preferences', methods=['GET', 'PATCH'])
@login_required
def user_preferences():
    """ Get user's preferences """
    connection = engine.connect()
    transaction = connection.begin()
    if request.method == 'GET':
        return_status = user.get_preferences(connection)
    if request.method == 'PATCH':
        return_status = user.patch_preferences(connection)
    transaction.commit()
    return return_status
