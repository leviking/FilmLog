""" Help Documentation Section (/help) """
from flask import render_template
from sqlalchemy.sql import text
from filmlog.config import app, engine

@app.route('/help', methods=['GET'])
def get_help():
    """ Index page for Help section """
    return render_template('help/index.html')

@app.route('/help/terms', methods=['GET'])
def terms():
    """ Terms of service """
    return render_template('help/terms.html')

@app.route('/help/films', methods=['GET'])
def get_filmtypes():
    """ Get a list of all the available films """
    connection = engine.connect()
    qry = text("""SELECT filmTypeID, brand, name, iso, kind
        FROM FilmTypes
        JOIN FilmBrands ON FilmBrands.filmBrandID = FilmTypes.filmBrandID
        ORDER BY brand, name, iso, kind""")
    filmtypes = connection.execute(qry).fetchall()
    return render_template('help/films.html', filmtypes=filmtypes)
