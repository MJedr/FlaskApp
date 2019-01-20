from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField, DateField, TimeField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo, Length
from app.models import Artist
from werkzeug.datastructures import MultiDict
import datetime

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')


class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField(
        'Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

    def validate_username(selfself, username):
        user = Artist.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Please use a different username.')

    def validate_email(self, email):
        user = Artist.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Please use another email adress.')

class GroupCreationForm(FlaskForm):
    groupname = StringField('Groupname', validators=[DataRequired()])
    description = StringField('Description', validators=[DataRequired()])
    submit = SubmitField('Create')

class EditProfileForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    about_me = TextAreaField('About me', validators=[Length(min=0, max=140)])
    submit = SubmitField('Submit')

    def __init__(self, original_username, *args, **kwargs):
        super(EditProfileForm, self).__init__(*args, **kwargs)
        self.original_username = original_username

    def validate_username(self, username):
        if username.data != self.original_username:
            user = Artist.query.filter_by(username=self.username.data).first()
            if user is not None:
                raise ValidationError('Please use a different username.')

class AddEventForm(FlaskForm):
    eventname = StringField('Name', validators=[DataRequired()])
    date = DateField('Date', format='%Y-%m-%d', validators=[DataRequired("Please enter the event fate in format YYYY-MM-DD.")])
    location = StringField('Venue', validators=[DataRequired()])
    description = TextAreaField('Description', validators=[DataRequired()])
    price = BooleanField('Free', validators=[DataRequired()])
    submit = SubmitField('Create')


class AddGroupPostForm(FlaskForm):
    post = TextAreaField('Please, type your message:', validators=[Length(min=0, max=140)])
    submit = SubmitField('Submit')