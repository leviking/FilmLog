import configparser
import os
import re

from flask import Flask
from flask_wtf.csrf import CSRFProtect
from filmlog import database

app = Flask('filmlog')
engine = database.engine

config = configparser.ConfigParser()
config.read(os.path.join(os.path.abspath(os.path.dirname(__file__)), '../config.ini'))

app.secret_key = config.get('session', 'secret_key')
app.config['TESTING'] = config.getboolean('app', 'testing')
app.debug = config.getboolean('app', 'debug')

user_files = os.path.join(os.path.abspath(os.path.dirname(__file__)),
                          config.get('files', 'user_files'))

app.config['ALLOWED_EXTENSIONS'] = set(['jpg', 'jpeg'])
app.config['UPLOAD_FOLDER'] = user_files
app.config['THUMBNAIL_SIZE'] = config.get('files', 'thumbnail_size')

app.config['RECAPTCHA_PUBLIC_KEY'] = config.get('recaptcha', 'public_key')
app.config['RECAPTCHA_PRIVATE_KEY'] = config.get('recaptcha', 'private_key')

# Global CSRF Protection
csrf = CSRFProtect(app)
