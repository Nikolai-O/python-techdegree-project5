from flask_wtf import Form
from wtforms import StringField, TextField, DateTimeField, TextAreaField
from wtforms.validators import DataRequired, Regexp, ValidationError

from models import Entry


def title_exists(form, field):
    if Entry.select().where(Entry.title == field.data).exists():
        raise ValidationError('Entry with that name already exists.')


class NewEntry(Form):
    title = TextField(
        'Title: ',
        validators=[
            DataRequired(),
            ])
    date = DateTimeField(
        'Date (format YYYY-MM-DD): ', format='%Y-%m-%d',
        validators=[]
    )
    time_spent = TextField(
        'Time spent on subject in hours (Please enter a number): ',
        validators=[
            DataRequired(),
            Regexp(r'^[0-9]+$', message="Time spent should be numbers only")
            ])
    learned = TextAreaField(
        'Tell us what you learned: ',
        validators=[DataRequired()]
    )
    ressources = TextAreaField(
        'List the ressources used for your learning: ',
        validators=[DataRequired()]
    )
    tags = StringField(
        'Enter tags for your entry (no commas, each white space creates new tag): ',
        validators=[DataRequired(),
        Regexp(r'^[a-zA-Z0-9_ ]+$',
        message=("Tags should be letters, "
        "numbers and underscores only, seperated by a space"))
    ])
