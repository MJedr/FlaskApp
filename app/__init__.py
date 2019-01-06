from flask import Flask, render_template, flash, url_for, redirect
from flask_bootstrap import Bootstrap
from app.forms import LoginForm
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from config import config


bootstrap = Bootstrap()
db = SQLAlchemy()
migrate = Migrate()

def create_app(config_name):
    app=Flask(__name__)
    config_name = 'default'
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)
    db.init_app(app)
    migrate.init_app(app, db)
    bootstrap.init_app(app)

    from app import models
    @app.route('/')
    @app.route('/index')
    def index():
        user = {'name': 'Marcjanna'}
        return render_template('base.html', user=user)

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        form = LoginForm()
        if form.validate_on_submit():
            flash('Login requested for user {}, remember_me={}'.format(
                form.username.data, form.remember_me.data))
            return redirect(url_for('index'))
        return render_template('login.html', title='Sign In', form=form)

    return app
