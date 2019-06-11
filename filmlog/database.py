""" Database setup """
import os
import configparser
from flask import Flask
from sqlalchemy import create_engine

app = Flask('filmlog')

config = configparser.ConfigParser()
config.read(os.path.join(os.path.abspath(os.path.dirname(__file__)), '../config.ini'))

app.config['SQLALCHEMY_DATABASE_URI'] = config.get('database', 'url')

engine = create_engine(config.get('database', 'url'),
                       pool_recycle=config.getint('database', 'pool_recycle'))
