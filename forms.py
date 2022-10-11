from flask_wtf import FlaskForm
from wtforms import Form, StringField, PasswordField, BooleanField, SubmitField   
from wtforms.validators import DataRequired

class LoginForm (FlaskForm):
    email = StringField('Correo electrónico', validators=[DataRequired(message = 'Debe ingresar un correo electrónico válido')])
    password =PasswordField('Contraseña', validators=[DataRequired('Password incorrecto')])
    remember = BooleanField('Recordar usuario')
    submit = SubmitField('Iniciar sesion')


class RegisterForm (FlaskForm):
    name = StringField('Nombres', validators=[DataRequired(message = 'Debe ingresar un nombre válido')])
    email = StringField('Correo electrónico', validators=[DataRequired(message = 'Debe ingresar un correo electrónico válido')])
    password =PasswordField('Contraseña')
    confirmPassword = PasswordField('Confirmar contraseña')
    submit = SubmitField('Registrarse')