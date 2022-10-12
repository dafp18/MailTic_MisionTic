from flask_wtf import FlaskForm
from wtforms import Form, StringField, PasswordField, BooleanField, SubmitField, EmailField, TextAreaField   
from wtforms.validators import DataRequired


class LoginForm (FlaskForm):
    email = EmailField('Correo electrónico', validators=[DataRequired(message = 'Debe ingresar un correo electrónico válido')])
    password =PasswordField('Contraseña', validators=[DataRequired('Password incorrecto')])
    remember = BooleanField('Recordar usuario')
    submit = SubmitField('Iniciar sesion')


class RegisterForm (FlaskForm):
    name = StringField('Nombres', validators=[DataRequired(message = 'Debe ingresar un nombre válido')])
    email = EmailField('Correo electrónico', validators=[DataRequired(message = 'Debe ingresar un correo electrónico válido')])
    password =PasswordField('Contraseña')
    confirmPassword = PasswordField('Confirmar contraseña')
    submit = SubmitField('Registrarse')


class NewMessageForm (FlaskForm):
    to = EmailField('Para', validators=[DataRequired(message = 'Debe ingresar un correo electrónico válido')])
    subject = StringField('Asunto', validators=[DataRequired(message = 'Debe ingresar un asunto')])
    message =TextAreaField('Mensaje')
    submitBtn = SubmitField('Enviar mensaje')    