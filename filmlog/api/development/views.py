""" Main view for Development part of API """
from flask_login import login_required
from flask import request

# Filmlog
from filmlog.api.development import api_dev_blueprint, developers

from filmlog.config import engine

@api_dev_blueprint.route('/', methods=['GET'])
def index():
    """ Index page for Development part of API """
    return "Hello"

# Developers
@api_dev_blueprint.route('/developers/', methods=['GET'])
@login_required
def developers_all():
    """ Get all developers """
    connection = engine.connect()
    transaction = connection.begin()
    if request.method == 'GET':
        return_status = developers.get_all(connection)
    transaction.commit()
    return return_status

## Developer (Singular)
@api_dev_blueprint.route('/developers/<int:developerID>', methods=['GET'])
def developer(developerID):
    """ Get a developer """
    connection = engine.connect()
    transaction = connection.begin()
    if request.method == 'GET':
        return_status = developers.get(connection, developerID)
    transaction.commit()
    return return_status

## Developer Logs
@api_dev_blueprint.route('/developers/<int:developerID>/logs', methods=['GET'])
def developer_logs(developerID):
    """ Get a developer """
    connection = engine.connect()
    transaction = connection.begin()
    if request.method == 'GET':
        return_status = developers.get_logs(connection, developerID)
    transaction.commit()
    return return_status
