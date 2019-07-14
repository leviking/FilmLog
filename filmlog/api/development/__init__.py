""" Init for API section """
from flask import Blueprint

api_dev_blueprint = Blueprint('api/development', __name__)

# pylint: disable=wrong-import-position
# This doesn't work without first setting the above.
# It is probably fixable but it works for now.
from filmlog.api.development import views
