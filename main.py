import functools
from flask import Flask,request,render_template,flash, redirect, url_for, g, make_response, session
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3 as sql
import os
import forms
import utils


SECRET_KEY = os.urandom(32)

app = Flask(__name__)
app.config['SECRET_KEY'] = SECRET_KEY


@app.route('/', methods=['GET','POST'])
def index():
    colorAlert = "alert-danger"
    title='Inicio'
    route = '/ Inicio'
    formRegister = forms.RegisterForm()
    formLogin = forms.LoginForm()

    if(formLogin.validate_on_submit() and request.method == 'POST'):
        email = formLogin.email.data
        password = formLogin.password.data
        con=sql.connect('database/MailTicDatabase.db')
        cur=con.cursor()
        user = cur.execute('select * from users where email = ? and password = ?', (email,password)).fetchone()
        
        if user is None:
            user = cur.execute('select * from users where email = ?', (email,)).fetchone()
            if user is None:
                flash('El correo electrónico no existe')
            else:
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
        
    return render_template('inicio.html', title=title, route=route, formLogin=formLogin,formRegister=formRegister,colorAlert=colorAlert )    
    

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
        return render_template('newMessage.html', title=title, route=route, formMessage=formMessage)
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
    if(formRegister.validate_on_submit() and request.method == 'POST'):
        try:
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
                        flash('Cuenta creada correctamente revisa tu correo para activarla.')
                except:
                    con.rollback()
                    flash('Upss ha ocurrido un error intente más tarde.')
                                    
                return render_template('inicio.html', title=title, route=route, formRegister=formRegister,colorAlert=colorAlert )
        except:
            return render_template('inicio.html', title=title, route=route, formLogin=formLogin,formRegister=formRegister,colorAlert=colorAlert )
    return render_template('inicio.html', title=title, route=route, formLogin=formLogin,formRegister=formRegister,colorAlert=colorAlert ) 

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
    return 'login'


def login_reqeuired(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('/'))
        
        return view(**kwargs)
    return wrapped_view


if __name__ == '__main__':    
    app.run(debug=True)