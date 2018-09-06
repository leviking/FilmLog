from flask_login import LoginManager, login_required, current_user, login_user, UserMixin
from sqlalchemy.sql import select, text, func
from sqlalchemy.exc import IntegrityError
from filmlog import database, functions
from flask import Blueprint, jsonify, request, make_response
from flask_api import status
from filmlog.api import api_blueprint, binders, projects, filmstock
from filmlog import engine

# http://jsonapi.org/format/

@api_blueprint.route('/',   methods = ['GET'])
def index():
    return "Hello"

@api_blueprint.route('/binders',  methods = ['GET', 'POST'])
@login_required
def binders_all():
    connection = engine.connect()
    transaction = connection.begin()
    userID = current_user.get_id()
    if request.method == 'GET':
        status = binders.get_all(connection, transaction)
    if request.method == 'POST':
        status = binders.post(connection, transaction)
    transaction.commit()
    return status

@api_blueprint.route('/binders/<int:binderID>',  methods = ['GET', 'PATCH', 'DELETE'])
@login_required
def binder(binderID):
    connection = engine.connect()
    transaction = connection.begin()
    if request.method == 'GET':
        status = binders.get(connection, transaction, binderID)
    if request.method == 'PATCH':
        status = binders.patch(connection, transaction, binderID)
    if request.method == 'DELETE':
        status = binders.delete(connection, transaction, binderID)
    transaction.commit()
    return status

@api_blueprint.route('/binders/<int:binderID>/projects',  methods = ['GET'])
@login_required
def projects_all(binderID):
    connection = engine.connect()
    transaction = connection.begin()

    if request.method == 'GET':
        status = projects.get_all(connection, transaction, binderID)
    transaction.commit()
    return status


@api_blueprint.route('/filmstock',  methods = ['GET'])
@login_required
def filmstock_all():
    connection = engine.connect()
    transaction = connection.begin()

    if request.method == 'GET':
        status = filmstock.get_all(connection, transaction)
    transaction.commit()
    return status

@api_blueprint.route('/filmstock/<int:filmTypeID>/<int:filmSizeID>',  methods = ['GET', 'PATCH'])
@login_required
def filmstock_details(filmTypeID, filmSizeID):
    connection = engine.connect()
    transaction = connection.begin()

    if request.method == 'GET':
        status = filmstock.get(connection, transaction, filmTypeID, filmSizeID)
    if request.method == 'PATCH':
        status = filmstock.patch(connection, transaction, filmTypeID, filmSizeID)
    transaction.commit()
    return status
