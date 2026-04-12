from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed, MultipleFileField
from wtforms import EmailField, PasswordField, SelectField, StringField, SubmitField
from wtforms.validators import DataRequired, Email, Length, Optional


class LoginForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired(), Length(max=80)])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Login")


class ClassRoomForm(FlaskForm):
    class_name = StringField("Class Name", validators=[DataRequired(), Length(max=100)])
    section = StringField("Section", validators=[DataRequired(), Length(max=30)])
    subject = StringField("Subject", validators=[Optional(), Length(max=120)])
    submit = SubmitField("Save Class")


class StudentForm(FlaskForm):
    student_id = StringField("Student ID", validators=[DataRequired(), Length(max=50)])
    full_name = StringField("Full Name", validators=[DataRequired(), Length(max=150)])
    email = EmailField("Email", validators=[DataRequired(), Email(), Length(max=120)])
    phone = StringField("Phone", validators=[DataRequired(), Length(max=20)])
    class_id = SelectField("Class", coerce=int, validators=[DataRequired()])
    images = MultipleFileField(
        "Upload Images",
        validators=[FileAllowed(["jpg", "jpeg", "png"], "Only image files are allowed.")],
    )
    submit = SubmitField("Save Student")


class ReportFilterForm(FlaskForm):
    attendance_date = StringField("Date", validators=[Optional()])
    class_id = SelectField("Class", coerce=int, validators=[Optional()], default=0)
    student_id = SelectField("Student", coerce=int, validators=[Optional()], default=0)
    submit = SubmitField("Filter")
