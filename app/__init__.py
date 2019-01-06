from flask import Flask, render_template, flash, url_for, redirect, request
from flask_bootstrap import Bootstrap
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from config import config
from flask_login import LoginManager, current_user, login_user, logout_user, login_required
from datetime import datetime



bootstrap = Bootstrap()
db = SQLAlchemy()
migrate = Migrate()
login = LoginManager()

def create_app(config_name):
    app = Flask(__name__)
    config_name = 'default'
    app.config.from_object(config[config_name])
    db.init_app(app)
    migrate.init_app(app, db)
    bootstrap.init_app(app)

    from app import models
    from app.forms import LoginForm, RegistrationForm, EditProfileForm
    from app.models import Artist, login
    login.init_app(app)


    @app.route('/')
    @app.route('/index')
    def index():
        return render_template('base.html')

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if current_user.is_authenticated:
            return redirect(url_for('index'))
        form = LoginForm()
        if form.validate_on_submit():
            user = Artist.query.filter_by(username=form.username.data).first()
            if user is None or not user.check_password(form.password.data):
                flash('Invalid username or password')
                return redirect(url_for('login'))
            login_user(user, remember=form.remember_me.data)
            return redirect(url_for('index'))
        return render_template('login.html', title='Sign In', form=form)

    @app.route('/register', methods=['GET', 'POST'])
    def register():
        if current_user.is_authenticated:
            return redirect(url_for('index'))
        form = RegistrationForm()
        if form.validate_on_submit():
            user = Artist(username=form.username.data, email=form.email.data)
            user.set_password(form.password.data)
            db.session.add(user)
            db.session.commit()
            flash('Congratulations, you are now a registered user!')
            return redirect(url_for('login'))
        return render_template('register.html', title='Register', form=form)

    @app.route('/user/<username>')
    @login_required
    def user(username):
        user = Artist.query.filter_by(username=username).first_or_404()
        posts = [
            {'author': user, 'body': 'Test post #1'},
            {'author': user, 'body': 'Test post #2'}
        ]
        return render_template('user.html', user=user)

    @app.before_request
    def before_request():
        if current_user.is_authenticated:
            current_user.last_seen = datetime.utcnow()
            db.session.commit()

    @app.route('/edit_profile', methods=['GET', 'POST'])
    @login_required
    def edit_profile():
        form = EditProfileForm()
        if form.validate_on_submit():
            current_user.username = form.username.data
            current_user.aboutMe = form.aboutMe.data
            db.session.commit()
            flash('Your changes have been saved.')
            return redirect(url_for('edit_profile'))
        elif request.method == 'GET':
            form.username.data = current_user.username
            form.about_me.data = current_user.aboutMe
        return render_template('edit_profile.html', title='Edit Profile',
                               form=form)

    return app


