from dataclasses import field
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, validators, ValidationError, EmailField
from wtforms.validators import DataRequired, Length, Email, EqualTo
import re
from wtforms.validators import ValidationError

def validate_student_email(form, field):
    pattern = r"^[a-zA-Z0-9._]+@student\.babcock\.edu\.ng$"
    if not re.match(pattern, field.data):
        raise ValidationError('Must be a valid student email')

def validate_lecturer_email(form, field):
    pattern = r"^[a-zA-Z0-9._]+@babcock\.edu\.ng$"
    if not re.match(pattern, field.data):
        raise ValidationError('Must be a valid lecturer email')

class StudentLoginForm(FlaskForm):
    email = EmailField('Email Address', validators=[DataRequired(), Email(), validate_student_email])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class LecturerLoginForm(FlaskForm):
    email = EmailField('Email Address', validators=[DataRequired(), Email(), validate_lecturer_email])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')
    
class NewSemesterForm(FlaskForm):
    semester_name = StringField('Semester Name', validators = [DataRequired()])
    academic_year = StringField('Academic Year', validators = [DataRequired()])
    submit = SubmitField('Create Semester')