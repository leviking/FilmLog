""" Configuration and Setup for the Filmlog """
import configparser
import os

from flask import Flask
from flask_wtf.csrf import CSRFProtect

from filmlog import database

app = Flask('filmlog')
engine = database.engine

# config = configparser.ConfigParser()
# Enable using env variables (e.g. for Dockerizing)
#config = configparser.SafeConfigParser(os.environ)
config = configparser.SafeConfigParser()
config.read(os.path.join(os.path.abspath(os.path.dirname(__file__)), '../config.ini'))

app.secret_key = config.get('session', 'secret_key')
app.config['TESTING'] = config.getboolean('app', 'testing')
app.debug = config.getboolean('app', 'debug')

user_files = os.path.join(os.path.abspath(os.path.dirname(__file__)),
                          config.get('files', 'user_files'))

kafka_enabled = config.getboolean('kafka', 'enabled')
kafka_topic = config.get('kafka', 'topic')
logging_use_flask = config.getboolean('logging', 'use_flask')
logging_use_kafka = config.getboolean('logging', 'use_kafka')
logging_kafka_key = config.get('logging', 'kafka_key')


app.config['ALLOWED_EXTENSIONS'] = set(['jpg', 'jpeg'])
app.config['UPLOAD_FOLDER'] = user_files
app.config['THUMBNAIL_SIZE'] = config.get('files', 'thumbnail_size')

app.config['RECAPTCHA_PUBLIC_KEY'] = config.get('recaptcha', 'public_key')
app.config['RECAPTCHA_PRIVATE_KEY'] = config.get('recaptcha', 'private_key')

# Global CSRF Protection
csrf = CSRFProtect(app)

kafka_producer = None
if kafka_enabled:
    from kafka import KafkaProducer
    kafka_producer = KafkaProducer(bootstrap_servers=config.get('kafka', 'bootstrap_servers'))
