FilmLog
=======

A simple web app to track film rolls and exposures and have an easy means to print them out for a physical log/negative file. 

Development Installation
------------------------

There are a few ways to install FilmLog currently. The current method
is to use a Python virtualenv and install Flask into it. Docker is also
an option though that method isn't quite as up to date. In both cases,
MariaDB 10.1 (or MySQL 5.6 may work) will need to be installed separately.

For now, let's go the virtualenv route:

  * In Your MariaDB/MySQL Installation, create a DB and user for FilmLog
    ```CREATE DATABASE FilmLogDev;
       GRANT ALL ON FilmLogDev.* TO 'FilmLog'@'localhost' IDENTIFIED BY 'password';```
  * Populate the DB by sourcing the `schema.sql` and `base-data.sql` files
    These are under the database directory along with a helper script
    you can optionally use. The script will populate the base schema, some
    sensible values for things like available films, and create a test user
    (the username and password are both 'dev') into a FilmLogDev database.
  * Install virtualenv for Python 2.6: 
    http://flask.pocoo.org/docs/0.12/installation/
  * Activate the virtualenv
    ```. venv/bin/activate```
    (Assuming you called your virtual env, `venv`)
  * Make sure you are in the project root then run
    ```pip install -r requirements.txt```
  * Copy config.ini.example to config.ini and fill in as appropriate
    If testing logins, you'll need to make sure Testing is true or you
    have Google Recaptcha keys generated. Otherwise toss in your DB
    information into the datbase url.
  * If all goes well, assuming your virtualenv is named `venv` you can
    simply run the wsgi.sh script in the root. It should start the
    app on http://localhost:5000.


