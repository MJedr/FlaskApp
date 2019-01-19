from flask import Flask, render_template, flash, url_for, redirect, request
from flask_bootstrap import Bootstrap
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy


from config import config
from flask_login import LoginManager, current_user, login_user, logout_user, login_required
from datetime import datetime
import logging
from logging.handlers import SMTPHandler
from logging.handlers import RotatingFileHandler
import os

bootstrap = Bootstrap()
db = SQLAlchemy()
migrate = Migrate()
login = LoginManager()

def create_app(config_name):
    app = Flask(__name__)
    config_name = 'default'
    app.config.from_object(config[config_name])
    app.secret_key = 'MarcysiaJestMistrzemProgramowania'
    db.init_app(app)
    migrate.init_app(app, db)
    bootstrap.init_app(app)

    from app import models
    from app.forms import LoginForm, RegistrationForm, EditProfileForm, GroupCreationForm, AddEventForm, AddGroupPostForm
    from app.models import Artist, login, Group, Event, Post, members
    login.init_app(app)


    @app.route('/')
    @app.route('/index')
    def index():
        return render_template('base.html')

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

    @app.route('/logout')
    def logout():
        if current_user.is_authenticated:
            logout_user()
            return redirect(url_for('index'))


    @app.route('/groups')
    @login_required
    def group_list():
        groups = Group.query.all()
        return render_template("groups/groups.html",
                               title="Groups",
                               groups=groups,
                               user=current_user)

    @app.route('/group/<groupname>',methods=['GET', 'POST'])
    @login_required
    def group_details(groupname):
        group = Group.query.filter_by(groupName=groupname).first_or_404()
        form=AddGroupPostForm()
        posts = Post.query.filter_by(post_group=group.id).all()
        group_members = db.session.query(members).filter_by(group_id=group.id).all()
        return render_template('groups/group_details.html', group=group,
                               members=group_members,
                               user=current_user,
                               form=form,
                               posts=posts)

    @app.route('/group/new',methods=['GET', 'POST'])
    @login_required
    def new_group():
        if current_user.is_authenticated:
            form = GroupCreationForm()
            if form.validate_on_submit():
                group = Group(groupName=form.groupname.data,
                              groupDescription=form.description.data,
                              admin=current_user.id)
                db.session.add(group)
                db.session.commit()
                flash('You have succesfully created a group')
                return redirect(url_for('group_list'))
            return render_template('groups/create_group.html',
                                   title='New Group', form=form)

    @app.route('/users')
    @login_required
    def users():
        artists = Artist.query.all()
        return render_template('users/users.html', artists=artists)

    @app.route('/user/<username>')
    @login_required
    def user_details(username):
        user = Artist.query.filter_by(username=username).first_or_404()
        return render_template('users/user_details.html', user=user)

    @app.before_request
    def before_request():
        if current_user.is_authenticated:
            current_user.last_seen = datetime.utcnow()
            db.session.commit()

    @app.route('/edit_profile', methods=['GET', 'POST'])
    @login_required
    def edit_profile():
        form = EditProfileForm(current_user.username)
        if form.validate_on_submit():
            current_user.username = form.username.data
            current_user.aboutMe = form.about_me.data
            db.session.commit()
            flash('Your changes have been saved.')
            return redirect(url_for('edit_profile'))
        elif request.method == 'GET':
            form.username.data = current_user.username
            form.about_me.data = current_user.aboutMe
        return render_template('edit_profile.html', title='Edit Profile',
                               form=form)

    @app.errorhandler(401)
    def unauthorized_error(error):
        return render_template('errors/401.html'), 401

    @app.errorhandler(404)
    def not_found_error(error):
        return render_template('errors/404.html'), 404

    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return render_template('errors/500.html'), 500

    @app.route('/join/<group>')
    @login_required
    def join_group(group):
        group = Group.query.filter_by(groupName=group).first()
        if group is None:
            flash('User {} not found.'.format(group))
            return redirect(url_for('index'))
        current_user.join_group(group)
        db.session.commit()
        flash('You are now a member of {}!'.format(group))
        return redirect(url_for('index', username=current_user.username))

    @app.route('/quit/<group>')
    @login_required
    def quit_group(group):
        group = Group.query.filter_by(groupName=group).first()
        if group is None:
            flash('User {} not found.'.format(group))
            return redirect(url_for('groups'))
        current_user.quit(group)
        db.session.commit()
        flash('You are not following {}.'.format(group))
        return redirect(url_for('groups', username=current_user.username))

    @app.route('/events')
    @login_required
    def events():
        events = Event.query.all()
        return render_template('events/events.html', events=events)

    @app.route('/addevent/<group>', methods=['GET', 'POST'])
    @login_required
    def add_event(group):
        group = Group.query.filter_by(groupName=group).first()
        if group is None:
            flash('User {} not found.'.format(group))
            return redirect(url_for('index'))
        is_member = db.session.query(members).filter_by(
            group_id=group.id,
            artist_id=current_user.id).all()
        if len(is_member)==0:
            flash('User {} not authorized to add event for the group.'.format(
                current_user))
            return redirect(url_for('index'))
        eventform = AddEventForm()
        if eventform.validate_on_submit():
            event = Event(eventName=eventform.eventname.data,
                          date=eventform.date.data,
                          location=eventform.location.data,
                          isFree=eventform.price.data,
                          eventDescription=eventform.description.data,
                          event_author=group.id)
            db.session.add(event)
            db.session.commit()
            flash('You have succesfully created a group')
            return redirect(url_for('group_list'))
        return render_template('events/add_event.html',
                               title='New Group', form=eventform)

    @app.route('/event_details/<eventname>')
    @login_required
    def event_details(eventname):
        event = Event.query.filter_by(eventName=eventname).first_or_404()
        return render_template('events/event_details.html', event=event)


    if not app.debug:
        if app.config['MAIL_SERVER']:
            auth = None
            if app.config['MAIL_USERNAME'] or app.config['MAIL_PASSWORD']:
                auth = (app.config['MAIL_USERNAME'], app.config['MAIL_PASSWORD'])
            secure = None
            if app.config['MAIL_USE_TLS']:
                secure = ()
            mail_handler = SMTPHandler(
                mailhost=(app.config['MAIL_SERVER'], app.config['MAIL_PORT']),
                fromaddr='no-reply@' + app.config['MAIL_SERVER'],
                toaddrs=app.config['ADMINS'], subject='Microblog Failure',
                credentials=auth, secure=secure)
            mail_handler.setLevel(logging.ERROR)
            app.logger.addHandler(mail_handler)
            if not os.path.exists('logs'):
                os.mkdir('logs')
            file_handler = RotatingFileHandler('logs/microblog.log', maxBytes=10240,
                                               backupCount=10)
            file_handler.setFormatter(logging.Formatter(
                '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
            file_handler.setLevel(logging.INFO)
            app.logger.addHandler(file_handler)

            app.logger.setLevel(logging.INFO)
            app.logger.info('Microblog startup')

    return app


