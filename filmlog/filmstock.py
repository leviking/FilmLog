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
        if request.form.get('button') == 'increment':
            if request.form.get('filmTypeID') != '' and request.form.get('filmSizeID') != '':
                qry = text("""UPDATE FilmStock SET qty = qty + 1
                    WHERE filmTypeID = :filmTypeID
                    AND filmSizeID = :filmSizeID
                    AND userID = :userID""")
                connection.execute(qry,
                                   filmTypeID=request.form.get('filmTypeID'),
                                   filmSizeID=request.form.get('filmSizeID'),
                                   userID=userID)
        if request.form.get('button') == 'decrement':
            if request.form.get('filmTypeID') != '' and request.form.get('filmSizeID') != '':
                qry = text("""SELECT qty FROM FilmStock
                    WHERE filmTypeID = :filmTypeID
                    AND filmSizeID = :filmSizeID
                    AND userID = :userID""")
                result = connection.execute(qry,
                                            filmTypeID=request.form.get('filmTypeID'),
                                            filmSizeID=request.form.get('filmSizeID'),
                                            userID=userID).fetchone()
                if result.qty == 1:
                    qry = text("""DELETE FROM FilmStock
                        WHERE filmTypeID = :filmTypeID
                        AND filmSizeID = :filmSizeID
                        AND userID = :userID""")
                    connection.execute(qry,
                                       filmTypeID=request.form.get('filmTypeID'),
                                       filmSizeID=request.form.get('filmSizeID'),
                                       userID=userID)
                else:
                    qry = text("""UPDATE FilmStock SET qty = qty - 1
                        WHERE filmTypeID = :filmTypeID
                        AND filmSizeID = :filmSizeID
                        AND userID = :userID""")
                    connection.execute(qry,
                                       filmTypeID=request.form.get('filmTypeID'),
                                       filmSizeID=request.form.get('filmSizeID'),
                                       userID=userID)
        if request.form.get('button') == 'add':
            qty = request.form.get('qty')
            if request.form.get('filmTypeID') != '':
                if qty != '':
                    qty = int(qty)
                    qry = text("""REPLACE INTO FilmStock
                        (filmTypeID, filmSizeID, userID, qty)
                        VALUES (:filmTypeID, :filmSizeID, :userID, :qty)""")
                    result = connection.execute(qry,
                                                filmTypeID=form.filmTypeID.data,
                                                filmSizeID=form.filmSizeID.data,
                                                qty=form.qty.data,
                                                userID=userID)
    qry = text("""SELECT FilmStock.filmTypeID AS filmTypeID,
        FilmStock.filmSizeID AS filmSizeID, FilmSizes.size AS size, qty,
        FilmBrands.brand AS brand, FilmTypes.name AS type, iso
        FROM FilmStock
        JOIN FilmTypes ON FilmTypes.filmTypeID = FilmStock.filmTypeID
        JOIN FilmBrands ON FilmBrands.filmBrandID = FilmTypes.filmBrandID
        JOIN FilmSizes ON FilmSizes.filmSizeID = FilmStock.filmSizeID
        WHERE FilmSizes.type = 'Small'
        AND userID = :userID
        AND qty != 0
        ORDER BY size, brand, type, iso""")
    stock_35mm = connection.execute(qry, userID=userID).fetchall()

    qry = text("""SELECT FilmStock.filmTypeID AS filmTypeID,
        FilmStock.filmSizeID AS filmSizeID, FilmSizes.size AS size, qty,
        FilmBrands.brand AS brand, FilmTypes.name AS type, iso
        FROM FilmStock
        JOIN FilmTypes ON FilmTypes.filmTypeID = FilmStock.filmTypeID
        JOIN FilmBrands ON FilmBrands.filmBrandID = FilmTypes.filmBrandID
        JOIN FilmSizes ON FilmSizes.filmSizeID = FilmStock.filmSizeID
        WHERE FilmSizes.type = 'Medium'
        AND userID = :userID
        AND qty != 0
        ORDER BY size, brand, type, iso""")
    stock_mf = connection.execute(qry, userID=userID).fetchall()

    qry = text("""SELECT FilmStock.filmTypeID AS filmTypeID,
        FilmStock.filmSizeID AS filmSizeID, FilmSizes.size AS size, qty,
        FilmBrands.brand AS brand, FilmTypes.name AS type, iso
        FROM FilmStock
        JOIN FilmTypes ON FilmTypes.filmTypeID = FilmStock.filmTypeID
        JOIN FilmBrands ON FilmBrands.filmBrandID = FilmTypes.filmBrandID
        JOIN FilmSizes ON FilmSizes.filmSizeID = FilmStock.filmSizeID
        WHERE FilmSizes.type = 'Large'
        AND userID = :userID
        AND qty != 0
        ORDER BY size, brand, type, iso""")
    stock_sheets = connection.execute(qry, userID=userID).fetchall()

    qry = text("""SELECT FilmTypes.filmTypeID AS filmTypeID,
        FilmBrands.brand AS brand, FilmTypes.name AS type, iso
        FROM FilmTypes
        JOIN FilmBrands ON FilmBrands.filmBrandID = FilmTypes.filmBrandID""")
    films = connection.execute(qry).fetchall()

    transaction.commit()
    return render_template('filmstock.html',
                           form=form,
                           stock_35mm=stock_35mm,
                           stock_mf=stock_mf,
                           stock_sheets=stock_sheets,
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
