from distutils.log import debug
import functools
from flask import Flask,request,render_template,flash, redirect, url_for, g, make_response, session, Markup
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3 as sql
import os
import forms
import utils
import random
from flask_mail import Mail
from flask_mail import Message

SECRET_KEY = os.urandom(32)
MAIL_SERVER = 'smtp-mail.outlook.com'
MAIL_PORT = 587
MAIL_USE_SSL = False
MAIL_USE_TLS = True
MAIL_USERNAME = 'pinzonad@uninorte.edu.co'
MAIL_PASSWORD = 'Facil2022'

app = Flask(__name__)
app.config['SECRET_KEY'] = SECRET_KEY
app.config['MAIL_SERVER'] = MAIL_SERVER
app.config['MAIL_PORT'] = MAIL_PORT
app.config['MAIL_USE_SSL'] = MAIL_USE_SSL
app.config['MAIL_USE_TLS'] = MAIL_USE_TLS
app.config['MAIL_USERNAME'] = MAIL_USERNAME
app.config['MAIL_PASSWORD'] = MAIL_PASSWORD
mail = Mail()

@app.route('/', methods=['GET','POST'], endpoint='login')
def index():
    colorAlert = "alert-danger"
    title='Inicio'
    route = '/ Inicio'
    formRegister = forms.RegisterForm()
    formLogin = forms.LoginForm()
    forgotPasswordForm = forms.forgotPasswordForm()
    
    if(formLogin.validate_on_submit() and request.method == 'POST'):
        email = formLogin.email.data
        password = formLogin.password.data
        con=sql.connect('database/MailTicDatabase.db')
        cur=con.cursor()
        user = cur.execute("select * from users where email = ? and password = ? and isActive = '1'", (email,password)).fetchone()

        if user is None:
            user = cur.execute('select * from users where email = ?', (email,)).fetchone()
            if user is None:
                flash('El correo electrónico no existe')
            else:
                if user[5] == '0':
                    flash('Debe activar la cuenta para poder ingresar')
                    return render_template('inicio.html', title=title, route=route, formLogin=formLogin,formRegister=formRegister,forgotPasswordForm=forgotPasswordForm,colorAlert=colorAlert )
                
                pass_almacenado = user[3]
                resultado = check_password_hash(pass_almacenado,password)
                if resultado is False:
                    flash('La contraseña es incorrecta')
                else:
                    session.clear()
                    session['user_id'] = user[0]
                    res = make_response(redirect(url_for('welcome')))
                    return res
        else:
            session.clear()
            session['user_id'] = user[0]
            return redirect(url_for('welcome'))    

    return render_template('inicio.html', title=title, route=route, formLogin=formLogin,formRegister=formRegister,forgotPasswordForm=forgotPasswordForm,colorAlert=colorAlert )    
    
@app.route('/forgotPassword', methods=['GET', 'POST'])
def forgotPassword():
    colorAlert = "alert-danger"
    title='Inicio'
    route = '/ Inicio'
    origen = 'forgot_password'
    formLogin = forms.LoginForm()
    formRegister = forms.RegisterForm()
    forgotPasswordForm = forms.forgotPasswordForm()
    if(forgotPasswordForm.validate_on_submit()):
        emailRecover = forgotPasswordForm.email.data
        colorAlert = "alert-success"
        con=sql.connect('database/MailTicDatabase.db')
        cur=con.cursor()
        cur.execute('INSERT INTO recoverPassword ( email,code) values (?,?)', (emailRecover,random.randint(1000, 9999)))
        con.commit()

        msg = Message('MailTic Recuperación de contraseña' , sender = app.config['MAIL_USERNAME'], recipients= [emailRecover])
        msg.html = render_template('email.html', email=emailRecover, origen=origen)
        mail.send(msg)
        flash('Hemos enviado un enlace de recuperación al correo electrónico proporcionado')

    return render_template('inicio.html', title=title, route=route, formLogin=formLogin,formRegister=formRegister,forgotPasswordForm=forgotPasswordForm,colorAlert=colorAlert ) 

@app.route('/recoverPassword/<email>', methods=['GET','POST'])
def recoverPassword(email):
    title='Recuperar contraseña'
    route = '/ Recuperar contraseña'
    colorAlert = "alert-danger"
    redirectLogin = False
    formRecoverPassword = forms.recoverPasswordForm()
    if(formRecoverPassword.validate_on_submit()):
        newPassword = formRecoverPassword.password.data
        confirmPassword = formRecoverPassword.confirmPassword.data

        if newPassword == confirmPassword:
            if not utils.isPasswordValid(newPassword):
                flash('La contraseña debe contener al menos 8 caracteres una letra mayúscula, un número y un símbolo')
            else:
                con=sql.connect('database/MailTicDatabase.db')
                cur=con.cursor()
                verifyEmailRestore = cur.execute('select * from recoverPassword where email = ?', (email,)).fetchone()
                if verifyEmailRestore is None:
                    flash('Upss! Ha ocurrido un error debe solicitar un nuevo enlace de recuperación')
                else:
                    colorAlert = "alert-success"                   
                    cur.execute( "update users set password = ? where email = ?", (generate_password_hash(newPassword),email) )
                    con.commit()
                    cur.execute( "delete from recoverPassword where email = ?", (email,) )
                    con.commit()
                    flash(Markup('Contraseña reestablecida correctamente. <br><a href="/" style="color:green"> <u><strong>Iniciar sesión </strong></u></a>'))
                    return render_template('recoverPassword.html', title=title, route=route,formRecoverPassword=formRecoverPassword,colorAlert=colorAlert)
        else:
            flash('Las contraseñas no coinciden')

    return render_template('recoverPassword.html', title=title, route=route,formRecoverPassword=formRecoverPassword,colorAlert=colorAlert)


@app.route('/welcome')
def welcome():
    title='Bienvenida'
    route = '/ Bienvenida'
    if 'user_id' in session:
        return render_template('bienvenida.html', title=title, route=route)
    else:
        return 'unAuthorized'

@app.route('/newMessage', methods=['GET','POST'])
def newMessage():
    title = 'Mensaje nuevo'
    route = '/ Mensaje nuevo'
    formMessage = forms.NewMessageForm()
    if 'user_id' in session:
        con=sql.connect('database/MailTicDatabase.db')
        cur=con.cursor()
        dirEmails = cur.execute('select distinct name, email from users').fetchall()
        return render_template('newMessage.html', title=title, route=route, formMessage=formMessage, dirEmails=dirEmails)
    else:
        return 'unAuthorized'

@app.route('/createMessage', methods=['GET','POST'])
def createMessage():
    formMessage = forms.NewMessageForm()
    if(formMessage.validate_on_submit()):
        to = formMessage.to.data
        subject = formMessage.subject.data
        message = formMessage.message.data
        con=sql.connect('database/MailTicDatabase.db')
        cur=con.cursor()
        user_to_id = cur.execute('select id from users where email = ?', (to,)).fetchone()
        if user_to_id is not None:
            user_to_id = user_to_id[0]
            cur.execute('INSERT INTO messages ( subject,message,id_user_to,id_user_from) values (?,?,?,?)', (subject,message,user_to_id,4))
            con.commit()
        else:
            flash('El correo electrónico de destino no existe') 
        
    return redirect(url_for('newMessage'))


@app.route('/messages')
def messages():
    title = 'Bandeja de entrada'
    route = '/ Bandeja de entrada'
    
    if 'user_id' in session:
        userSession = session['user_id']
        con=sql.connect('database/MailTicDatabase.db')
        cur=con.cursor()
        messages = cur.execute('select a.id as idmsg, a.subject, a.message, a.created_at, b.id as iduser, b.name, b.email from messages a inner join users b on b.id = id_user_to where id_user_to = ?', (userSession,)).fetchall()
        print(messages)
        return render_template('messages.html', title=title, route=route, messages=messages)
    else:
        return 'unAuthorized'

@app.route('/add_user', methods=['GET', 'POST'])
def add_user():
    colorAlert = "alert-danger"
    title='Inicio'
    route = '/ Inicio'
    formLogin = forms.LoginForm()
    formRegister = forms.RegisterForm()
    forgotPasswordForm = forms.forgotPasswordForm()
    if(formRegister.validate_on_submit() and request.method == 'POST'):
        try:
            origen = 'register_user'
            name = formRegister.name.data
            email = formRegister.email.data
            password = formRegister.password.data
            confirmPassword = formRegister.confirmPassword.data
            error = None
            
            if not utils.isEmailValid(email):
                error = 'Debe ingresar un correo electrónico válido'
                flash(error)

            if not utils.isPasswordValid(password):
                error = 'La contraseña debe contener al menos 8 caracteres una letra mayúscula, un número y un símbolo'
                flash(error)
            else:
                if(password != confirmPassword):
                    error = 'Las contraseñas no coinciden'    
                    flash(error)

            if not error:          
                colorAlert = "alert-success"
                try:
                    with sql.connect("database/MailTicDatabase.db") as con:
                        cur = con.cursor()                       
                        cur.execute( "INSERT INTO users ( name,email,password,id_rol ) VALUES ( ?,?,?,? )", (name,email,generate_password_hash(password),1) )
                        con.commit()

                        msg = Message('MailTic Bienvenido activemos tu cuenta!' , sender = app.config['MAIL_USERNAME'], recipients= [email])
                        msg.html = render_template('email.html', email=email, origen=origen)
                        mail.send(msg)
                        flash('Cuenta creada correctamente revisa tu correo para activarla.')
                except:
                    con.rollback()
                    flash('Upss ha ocurrido un error intente más tarde.')
                                    
                return render_template('inicio.html', title=title, route=route, formRegister=formRegister, forgotPasswordForm=forgotPasswordForm, colorAlert=colorAlert )    
        except:
            return render_template('inicio.html', title=title, route=route, formLogin=formLogin,formRegister=formRegister,forgotPasswordForm=forgotPasswordForm,colorAlert=colorAlert )
    return render_template('inicio.html', title=title, route=route, formLogin=formLogin,formRegister=formRegister,forgotPasswordForm=forgotPasswordForm,colorAlert=colorAlert ) 

@app.route('/activateAccount/<email>')
def activateAccount(email):
    con=sql.connect('database/MailTicDatabase.db')
    cur=con.cursor()
    cur.execute("update users set isActive = '1' where email = ? ", (email,))
    con.commit()
    return 'cuenta activada correctamente!' 


@app.route('/delete_msg/<idmsg>')
def delete_msg(idmsg):
    if 'user_id' in session:
        con=sql.connect('database/MailTicDatabase.db')
        cur=con.cursor()
        cur.execute('delete from messages where id = ?', (idmsg,))
        con.commit()
        return redirect(url_for('messages'))
    else:
        return 'unAuthorized'

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

def login_reqeuired(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('/'))
        
        return view(**kwargs)
    return wrapped_view


if __name__ == '__main__':  
    mail.init_app(app) 
    app.run(debug=True)
    