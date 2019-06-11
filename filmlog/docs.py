""" Help Documentation Section (/help) """
from flask import render_template
from filmlog.config import app

@app.route('/help', methods=['GET'])
def get_help():
    """ Index page for Help section """
    return render_template('help/index.html')

@app.route('/help/terms', methods=['GET'])
def terms():
    """ Terms of service """
    return render_template('help/terms.html')
