from flask import request, render_template, redirect, url_for, flash, abort
from sqlalchemy.sql import select, text, func
import os, re, string, random
from flask_login import LoginManager, login_user, logout_user, UserMixin

# Forms
from flask_wtf import FlaskForm, RecaptchaField
from wtforms import Form, StringField, PasswordField, validators
from wtforms.validators import DataRequired, Length

from werkzeug.security import generate_password_hash, \
     check_password_hash

from filmlog import app
from filmlog import database, engine
#from filmlog.functions import insert

### Functions
def generate_registration_code(size=64, chars=string.ascii_lowercase + string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))

### Classes
class User(UserMixin):
    def __init__(self, userID):
        self.id = userID

    def get_id(self):
        return unicode(self.id)

    def get(userID):
        return self.id

    def set_password(self, password_cleartest):
        self.password = generate_password_hash(password_cleartest)

    def check_password(self, password):
        return check_password_hash(self.password, password)

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[validators.input_required()])
    password = PasswordField('Password', validators=[validators.input_required()])

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[validators.input_required(), Length(min=1,max=64)])
    email = StringField('Email', validators=[validators.Optional(), Length(min=1,max=256)])
    password = PasswordField('Password', validators=[validators.input_required(),
        validators.EqualTo('password2', message='Passwords must match')])
    password2 = PasswordField('Re-Enter Password', validators=[validators.input_required()])
    recaptcha = RecaptchaField()

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

@login_manager.user_loader
def load_user(user_id):
    return User(user_id)

@login_manager.unauthorized_handler
def unauthorized():
    # do stuff
    return redirect("/login")

@app.route('/login', methods=['GET', 'POST'])
def login():
    connection = engine.connect()
    transaction = connection.begin()
    form = LoginForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            username = form.username.data
            password = form.password.data
            qry = text("""SELECT userID, password FROM Users
                    WHERE username = :username""")
            user = connection.execute(qry, username=username).fetchone()
            if user:
                if check_password_hash(user.password, password):
                    login_user(User(user.userID), remember=True)
                    qry = text("""UPDATE Users SET lastLogin = NOW()
                        WHERE userID = :userID""")
                    connection.execute(qry, userID=user.userID)
                    transaction.commit()
                    return redirect("/")
            transaction.rollback()
    return render_template('users/login.html', form=form)

@app.route('/logout', methods=['GET'])
def logout():
    logout_user()
    return redirect("/")

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            #qry = text("""(SELECT 1 from UsersUnverified WHERE username=:username)
            #    UNION
            #    (SELECT 1 FROM UsersUnverified WHERE email=:email)""")
            #unverified_users = engine.execute(qry,
            #    username=form.username.data,
            #    email=form.email.data).fetchall()
            #qry = text("""(SELECT 1 from Users WHERE username=:username)
            #    UNION
            #    (SELECT 1 FROM Users WHERE email=:email)""")
            #users = engine.execute(qry,
            #    username=form.username.data,
            #    email=form.email.data).fetchall()

            qry = text("""(SELECT 1 from UsersUnverified WHERE username=:username)""")
            unverified_users = engine.execute(qry,
                username=form.username.data).fetchall()
            qry = text("""(SELECT 1 from Users WHERE username=:username)""")
            users = engine.execute(qry,
                username=form.username.data).fetchall()
            if len(unverified_users) > 0 or len(users) > 0:
                flash("User already exists")
            else:
                #qry = text("""INSERT INTO UsersUnverified
                #    (username, email, password, registrationCode)
                #    VALUES (:username, :email, :password, :registrationCode)""")
                #engine.execute(qry,
                #    username=form.username.data,
                #    email=form.email.data,
                #    password=generate_password_hash(form.password.data),
                #    registrationCode=generate_registration_code())
                qry = text("""INSERT INTO Users
                    (username, password, createdOn)
                    VALUES (:username, :password, NOW())""")
                engine.execute(qry,
                    username=form.username.data,
                    password=generate_password_hash(form.password.data))
                return render_template("users/post_registration.html",
                    username = form.username.data)
        else:
            app.logger.info('User registration form has invalid data')
            flash("Looks like you did something wrong.")
    return render_template('users/register.html', form=form)
