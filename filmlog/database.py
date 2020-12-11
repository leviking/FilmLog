""" Database setup """
import os
import configparser
from flask import Flask
from sqlalchemy import create_engine

app = Flask('filmlog')

config = configparser.ConfigParser()
config.read(os.path.join(os.path.abspath(os.path.dirname(__file__)), '../config.ini'))

db_url = os.getenv('DB_URL')
if not db_url:
    db_url = config.get('database', 'url')

app.config['SQLALCHEMY_DATABASE_URI'] = db_url
app.config['SQLALCHEMY_POOL_PRE_PING'] = config.getboolean('database', 'pool_pre_ping')
engine = create_engine(db_url,
                       pool_recycle=config.getint('database', 'pool_recycle'),
                       pool_size=config.getint('database', 'pool_size'))
