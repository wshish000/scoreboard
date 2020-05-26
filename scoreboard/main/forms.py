from flask_wtf import FlaskForm
from wtforms import DateField, TextAreaField, SubmitField, SelectField, StringField, IntegerField, FloatField
from wtforms.validators import DataRequired, Length, Email,Regexp
from ..models import Role, User
from wtforms import ValidationError


class BasicForm(FlaskForm):
    number = StringField('Number', validators=[DataRequired(), Length(1, 64)])
    name = StringField('Name', validators=[DataRequired(), Length(1, 64), Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0,
                                                            'Usernames must have only letters, numbers, dots or underscores')])
    week = IntegerField('Week', validators=None)
    sit_up = IntegerField('SitUp', validators=None)
    pull_up = IntegerField('PullUp', validators=None)
    long_run = FloatField('LongRun', validators=None)
    retrace = FloatField('Retrace', validators=None)
    timestamp = DateField('Time', validators=None)

    submit = SubmitField('Submit')


class PostForm(FlaskForm):
    body = TextAreaField("What's on your mind", validators=[DataRequired()])
    submit = SubmitField('Submit')


class CommentForm(FlaskForm):
    body = StringField('Enter your comment', validators=[DataRequired()])
    submit = SubmitField('Submit')


class EditProfileAdminForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Length(1, 64), Email()])
    username = StringField('Username', validators=[DataRequired(), Length(1, 64), Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0,'Usernames must have only letters, numbers, dots or underscores')])
    role = SelectField('Role', coerce=int)
    submit = SubmitField('Submit')

    def __init__(self, user, *args, **kwargs):
        super(EditProfileAdminForm, self).__init__(*args, **kwargs)
        self.role.choices = [(role.id, role.name) for role in Role.query.order_by(Role.name).all()]
        self.user = user

    def validate_email(self, field):
        if field.data != self.user.email and User.query.filter_by(email=field.data).first():
            raise ValidationError('Email already registered.')

    def validate_username(self, field):
        if field.data != self.user.username and User.query.filter_by(username=field.data).first():
            raise ValidationError('Username already in use.')

