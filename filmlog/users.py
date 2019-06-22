""" User specific interactions, specifically logins """
from flask import request, render_template, redirect, flash
from sqlalchemy.sql import text
from flask_login import LoginManager, login_user, logout_user, UserMixin
from werkzeug.security import generate_password_hash, \
     check_password_hash

# Forms
from flask_wtf import FlaskForm, RecaptchaField
from wtforms import StringField, PasswordField, validators
from wtforms.validators import Length

# Filmlog
from filmlog.config import app, engine

### Functions
# def generate_registration_code(size=64, chars=string.ascii_lowercase + \
# string.ascii_uppercase + string.digits):
#    """ Generate an account registration code """
#    return ''.join(random.choice(chars) for _ in range(size))

### Classes
class User(UserMixin):
    """ User class """
    def __init__(self, userID):
        """ __init__, set the userID """
        self.id = userID

    def get_id(self):
        """ Return a string of the user ID """
        return str(self.id)

    def get(self):
        """ Return the user ID """
        return self.id

    # pylint: disable=attribute-defined-outside-init
    # May be a better way to handle this, but for now, logins work.
    def set_password(self, password_cleartest):
        """ Set the user's password """
        self.password = generate_password_hash(password_cleartest)

    def check_password(self, password):
        """ Check the password against the hash """
        return check_password_hash(self.password.decode(), password)

class LoginForm(FlaskForm):
    """ User login form """
    username = StringField('Username', validators=[validators.input_required()])
    password = PasswordField('Password', validators=[validators.input_required()])

class RegistrationForm(FlaskForm):
    """ New user registration form """
    username = StringField('Username', validators=[validators.input_required(),
                                                   Length(min=1, max=64)])
    email = StringField('Email', validators=[validators.input_required(),
                                             Length(min=1, max=256)])

    # pylint: disable=line-too-long
    # This is ugly, but will be uglier in multiple lines
    password = PasswordField('Password',
                             validators=[validators.input_required(),
                                         validators.EqualTo('password2', message='Passwords must match')])
    password2 = PasswordField('Re-Enter Password',
                              validators=[validators.input_required()])
    recaptcha = RecaptchaField()

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

@login_manager.user_loader
def load_user(user_id):
    """ Return a user of given user ID """
    return User(user_id)

@login_manager.unauthorized_handler
def unauthorized():
    """ User is not authorized """
    # do stuff
    return redirect("/login")

@app.route('/login', methods=['GET', 'POST'])
def login():
    """ Log a user in """
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
                if check_password_hash(user.password.decode(), password):
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
    """ Log a user out (clear the cookie) """
    logout_user()
    return redirect("/")

@app.route('/register', methods=['GET', 'POST'])
def register():
    """ Register a new user """
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
            if unverified_users or users:
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
                                       username=form.username.data)
        else:
            app.logger.info('User registration form has invalid data')
            flash("Looks like you did something wrong.")
    return render_template('users/register.html', form=form)
