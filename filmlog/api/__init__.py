""" Init for API section """
from flask import Blueprint

api_blueprint = Blueprint('api', __name__)

# pylint: disable=wrong-import-position
# This doesn't work without first setting the above.
# It is probably fixable but it works for now.
from filmlog.api import views
