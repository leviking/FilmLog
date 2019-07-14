""" Main view for Development part of API """
from dateutil.parser import parse

from flask import request
from flask_api import status
from flask_login import login_required

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
    """ Get developer logs """
    connection = engine.connect()
    transaction = connection.begin()
    startDate = None
    endDate = None
    if request.method == 'GET':
        if request.args.get('startDate'):
            try:
                parse(request.args.get('startDate'))
            except ValueError:
                return "FAILED", status.HTTP_400_BAD_REQUEST
            startDate = request.args.get('startDate')
        if request.args.get('endDate'):
            try:
                parse(request.args.get('endDate'))
            except ValueError:
                return "FAILED", status.HTTP_400_BAD_REQUEST
            endDate = request.args.get('endDate')
        return_status = developers.get_logs(connection, developerID, startDate, endDate)
    transaction.commit()
    return return_status

## Developer's Films Developed
@api_dev_blueprint.route('/developers/<int:developerID>/stats', methods=['GET'])
def developer_stats(developerID):
    """ Get a films developed """
    connection = engine.connect()
    transaction = connection.begin()
    if request.method == 'GET':
        return_status = developers.get_developer_stats(connection, developerID)
    transaction.commit()
    return return_status
