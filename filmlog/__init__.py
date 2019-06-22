""" Main setup for FilmLog application """

import os
import re
from datetime import date
from flask import Flask
from flask import abort, redirect, render_template
from sqlalchemy.dialects.mysql import INTEGER, SMALLINT
from flask_login import LoginManager, UserMixin
from werkzeug.utils import secure_filename
from flask_wtf.csrf import CSRFProtect
from filmlog import config
from filmlog import database
from filmlog import views
from filmlog.config import app, engine, csrf, user_files

# Error Handling
if not app.debug:
    @app.errorhandler(404)
    def page_not_found():
        """ Page Not Found """
        return render_template('errors/404.html'), 404

    @app.errorhandler(500)
    def internal_server_error(error):
        """ Internal Server Error Page """
        app.logger.error('Server Error: %s', (error))
        return render_template('errors/500.html'), 500

    @app.errorhandler(Exception)
    def unhandled_exception(error):
        """ Unhandled Exception Error """
        app.logger.error('Unhandled Exception: %s', (error))
        return render_template('errors/500.html'), 500

# Template Filters
@app.template_filter('to_date')
def _jinja2_filter_date(input_date):
    if input_date is None:
        return 'Unknown'
    date_format = '%Y-%m-%d'
    return input_date.strftime(date_format)

@app.context_processor
def section_mapping():
    """ Friendly Names For Sections """
    section_map = (
        ('/gear', 'Gear'),
        ('/developing', 'Developing'),
        ('/filmstock', 'Film Stock'),
        ('/filmtypes', 'Available Films'),
        ('/stats', 'Stats')
    )
    return dict(section_map=section_map)

if __name__ == "__main__":
    app.run(host='0.0.0.0')
