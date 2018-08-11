#!/usr/bin/env python
from os import listdir
from os.path import isfile, join, abspath, dirname, splitext
import ConfigParser

from filmlog import app

from sqlalchemy import create_engine
from sqlalchemy.sql import text
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base

config = ConfigParser.ConfigParser()
config.read(join(abspath(dirname(__file__)), './config.ini'))

migration_directory = 'database/migrations/'
app.config['SQLALCHEMY_DATABASE_URI'] = config.get('database', 'url')

engine = create_engine(config.get('database', 'url'),
    pool_recycle=config.getint('database', 'pool_recycle'))

connection = engine.connect()
completed_migrations = []
migration_files = []

# Find all our completed migrations, chuck them in a list
qry = text("""SELECT name FROM Migrations""")
result = connection.execute(qry)
for row in result:
    completed_migrations.append(row[0])

# Find all the migration files (those ending in .sql)
for f in listdir(migration_directory):
    if isfile(migration_directory + f):    
        if splitext(f)[1] == '.sql':
            migration_files.append(splitext(f)[0])

# Now find only the migrations that have not yet been run
to_migrate = set(migration_files) - set(completed_migrations)

# This should use a prepared statement, but since it's just a migration
# it didn't seem worth the extra effort
for migration in sorted(to_migrate):
    f = open(migration_directory + migration + '.sql')
    qry = f.read()
    try:
        result = connection.execute(qry)
    except Exception:
        print "Migration failed for %s" % migration
        f.close()
        break
    try:
        qry = text("""INSERT INTO Migrations (name) VALUES (:name)""")
        connection.execute(qry, name = migration)
    except Exception:
        print "Migration passed but failed to update Migrations table"
        f.close()
        break
    print "Migration %s passed" % migration
    f.close()
