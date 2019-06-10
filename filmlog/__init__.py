from flask import Flask
from flask import abort, redirect, render_template
from sqlalchemy.dialects.mysql import INTEGER, SMALLINT
from datetime import date
from flask_login import LoginManager, UserMixin
import ConfigParser
from werkzeug.utils import secure_filename
from flask_wtf.csrf import CSRFProtect

import os, re

app = Flask(__name__)

config = ConfigParser.ConfigParser()
config.read(os.path.join(os.path.abspath(os.path.dirname(__file__)), '../config.ini'))

app.secret_key = config.get('session', 'secret_key')
app.config['TESTING'] = config.getboolean('app', 'testing')
app.debug = config.getboolean('app', 'debug')


user_files = os.path.join(os.path.abspath(os.path.dirname(__file__)),
                          config.get('files', 'user_files'))

app.config['ALLOWED_EXTENSIONS'] = set(['jpg', 'jpeg'])
app.config['UPLOAD_FOLDER'] = user_files
app.config['THUMBNAIL_SIZE'] = config.get('files', 'thumbnail_size')

app.config['RECAPTCHA_PUBLIC_KEY'] = config.get('recaptcha','public_key')
app.config['RECAPTCHA_PRIVATE_KEY'] = config.get('recaptcha','private_key')

# Global CSRF Protection
csrf = CSRFProtect(app)

from filmlog import database
engine = database.engine

# Views
from filmlog import views

# Error Handling
if not app.debug:
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('errors/404.html'), 404

    @app.errorhandler(500)
    def internal_server_error(error):
        app.logger.error('Server Error: %s', (error))
        return render_template('errors/500.html'), 500

    @app.errorhandler(Exception)
    def unhandled_exception(e):
        app.logger.error('Unhandled Exception: %s', (e))
        return render_template('errors/500.html'), 500

# Template Filters
@app.template_filter('to_date')
def _jinja2_filter_date(date, fmt=None):
    if date is None:
        return 'Unknown'
    format='%Y-%m-%d'
    return date.strftime(format)

@app.context_processor
def section_mapping():
    section_map = (
        ('/gear', 'Gear'),
        ('/darkroom', 'Darkroom'),
        ('/developing', 'Developing'),
        ('/filmstock', 'Film Stock'),
        ('/filmtypes', 'Available Films'),
        ('/stats', 'Stats')
    )
    return dict(section_map=section_map)


if __name__ == "__main__":
    app.run(host='0.0.0.0')
