from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SelectField, SubmitField
from wtforms.validators import DataRequired


class UserForm(FlaskForm):
    username = StringField("Username: ", validators=[DataRequired()])
    # dept_id = IntegerField("Department Id: ", validators=[DataRequired()])
    dept_id = SelectField("User Role: ", choices=[('1', 'Staff'), ('9', 'Manager')], validators=[DataRequired()])
    login_ip = StringField("Login IP: ", validators=[DataRequired()])
    submit = SubmitField("Submit")