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
        super(FilmStockForm, self).__init__()
        self.connection = connection
        self.filmTypeID.choices = get_film_types(connection)
        self.filmSizeID.choices = get_film_sizes(connection)


@app.route('/filmstock', methods=['GET', 'POST'])
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
        FilmBrands.brand AS brand, FilmTypes.name AS type, iso
        FROM FilmTypes
        JOIN FilmBrands ON FilmBrands.filmBrandID = FilmTypes.filmBrandID""")
    films = connection.execute(qry).fetchall()

    transaction.commit()
    return render_template('filmstock.html',
                           form=form,
                           films=films)

@app.route('/filmtypes', methods=['GET'])
@login_required
def get_filmtypes():
    """ Get a list of all the available films """
    connection = engine.connect()
    qry = text("""SELECT filmTypeID, brand, name, iso, kind
        FROM FilmTypes
        JOIN FilmBrands ON FilmBrands.filmBrandID = FilmTypes.filmBrandID
        ORDER BY brand, name, iso, kind""")
    filmtypes = connection.execute(qry).fetchall()
    return render_template('filmtypes.html', filmtypes=filmtypes)
