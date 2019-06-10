from flask import Flask
from flask import request, render_template, redirect, url_for, flash, abort
from filmlog import config

app = config.app
engine = config.engine

@app.route('/help', methods=['GET', 'POST'])
def help():
    return render_template('help/index.html')

@app.route('/help/terms', methods = ['GET'])
def terms():
    return render_template('help/terms.html')
