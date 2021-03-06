""" Filmstock inventory section (/filmstock) """
from flask import request, render_template
from flask_login import login_required, current_user
from sqlalchemy.sql import text

# Forms
from flask_wtf import FlaskForm
from wtforms import SelectField, IntegerField
from wtforms.validators import DataRequired, Optional, NumberRange

# Filmlog
from filmlog.config import app, engine
from filmlog.functions import get_film_types, get_film_sizes

class FilmStockForm(FlaskForm):
    """ Film stock form """
    filmTypeID = SelectField('Film',
                             validators=[DataRequired()],
                             coerce=int)
    filmSizeID = SelectField('Film Size',
                             validators=[Optional()],
                             coerce=int)
    qty = IntegerField('Qty',
                       validators=[NumberRange(min=-32768, max=32767),
                                   DataRequired()])

    def __init__(self, connection):
        #super(FilmStockForm, self).__init__()
        #super(FilmStockForm).__init__()
        super().__init__()
        self.connection = connection
        self.filmTypeID.choices = get_film_types(connection)
        self.filmSizeID.choices = get_film_sizes(connection)

@app.route('/films', methods=['GET'])
@login_required
def films_index():
    """ Films Landing Page Index """
    return render_template('films/index.html')

@app.route('/films/<int:filmTypeID>', methods=['GET'])
@login_required
def film_details(filmTypeID):
    """ Get Film Details """
    return render_template('films/film.html',
                            filmTypeID=filmTypeID)

@app.route('/films/tests', methods=['GET'])
@login_required
def film_tests():
    """ Film Tests Page """
    return render_template('films/tests.html')

@app.route('/films/steptablets', methods=['GET'])
@login_required
def film_steptablets():
    """ User's Step Tablets Page """
    return render_template('films/steptablets.html')

@app.route('/films/steptablets/<int:stepTabletID>', methods=['GET'])
@login_required
# pylint: disable=unused-argument
# Argument needed by Javascript - html is just a template
def film_steptablet(stepTabletID):
    """ Step Tablet Details Page """
    return render_template('films/steptablet.html')

@app.route('/films/<int:filmTypeID>/tests/<int:filmTestID>', methods=['GET'])
@login_required
def film_test(filmTypeID, filmTestID):
    """ Get Film Test Details """
    return render_template('films/test.html',
                            filmTypeID=filmTypeID,
                            filmTestID=filmTestID)

@app.route('/films/stock', methods=['GET', 'POST'])
@login_required
def filmstock():
    """ Filmstock Index """
    connection = engine.connect()
    transaction = connection.begin()
    userID = current_user.get_id()
    form = FilmStockForm(connection)

    if request.method == 'POST':
        if request.form.get('button') == 'add':
            qty = request.form.get('qty')
            if request.form.get('filmTypeID') != '':
                if qty != '':
                    qty = int(qty)
                    qry = text("""REPLACE INTO FilmStock
                        (filmTypeID, filmSizeID, userID, qty)
                        VALUES (:filmTypeID, :filmSizeID, :userID, :qty)""")
                    connection.execute(qry,
                                       filmTypeID=form.filmTypeID.data,
                                       filmSizeID=form.filmSizeID.data,
                                       qty=form.qty.data,
                                       userID=userID)

    qry = text("""SELECT FilmTypes.filmTypeID AS filmTypeID,
        FilmTypes.name AS type, iso
        FROM FilmTypes
        WHERE userID = :userID""")
    films = connection.execute(qry, userID=userID).fetchall()

    transaction.commit()
    return render_template('films/stock.html',
                           form=form,
                           films=films)
