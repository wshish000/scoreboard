from flask_wtf import FlaskForm
from wtforms import DateField, IntegerField, SubmitField, SelectField, StringField, FloatField
from wtforms.validators import DataRequired, Length, Regexp
from ..models import Role, User
from wtforms import ValidationError


class EditProfileForm(FlaskForm):
    number = StringField('Number', validators=[DataRequired(), Length(1, 64)])
    name = StringField('Name', validators=[DataRequired(), Length(1, 64), Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0,'Usernames must have only letters, numbers, dots or underscores')])
    role = SelectField('Role', coerce=int)

    born_time = DateField('Born', validators=None)
    military_time = DateField('Military', validators=None)
    sex = IntegerField('Sex', validators=None)
    level = StringField('Level', validators=None)
    job = StringField('Job', validators=None)

    submit = SubmitField('Submit')

    def __init__(self, user, *args, **kwargs):
        super(EditProfileForm, self).__init__(*args, **kwargs)
        self.role.choices = [(role.id, role.name) for role in Role.query.order_by(Role.name).all()]
        self.user = user

    def validate_number(self, field):
        if field.data != self.user.number and User.query.filter_by(number=field.data).first():
            raise ValidationError('Number already registered.')

    def validate_name(self, field):
        if field.data != self.user.name and User.query.filter_by(name=field.data).first():
            raise ValidationError('Name already in use.')


class AddForm(FlaskForm):

    number = StringField('Number', validators=[DataRequired(), Length(1, 64)])
    name = StringField('Name', validators=[DataRequired(), Length(1, 64), Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0,'Usernames must have only letters, numbers, dots or underscores')])
    role = SelectField('Role', coerce=int)

    password = StringField('Password', validators=[DataRequired()])
    born_time = DateField('Born', validators=None)
    military_time = DateField('Military', validators=None)
    sex = IntegerField('Sex', validators=None)
    height = IntegerField('Height', validators=None)
    weight = FloatField('Weight', validators=None)
    level = StringField('Level', validators=None)
    job = StringField('Job', validators=None)

    submit = SubmitField('Submit')

    def __init__(self, *args, **kwargs):
        super(AddForm, self).__init__(*args, **kwargs)
        self.role.choices = [(role.id, role.name) for role in Role.query.order_by(Role.name).all()]

    def validate_number(self, field):
        if User.query.filter_by(number=field.data.lower()).first():
            raise ValidationError('Number already registered.')

    def validate_name(self, field):
        if User.query.filter_by(name=field.data).first():
            raise ValidationError('Name already in use.')
