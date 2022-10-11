from flask import Flask,request,render_template,flash
import os
SECRET_KEY = os.urandom(32)
import forms

app = Flask(__name__)
app.config['SECRET_KEY'] = SECRET_KEY

@app.route('/', methods=['GET','POST'])
def index():
    formLogin = forms.LoginForm()
    formRegister = forms.RegisterForm()
    if(formLogin.validate_on_submit()):
        flash('usuario {}, password {}, recordar {}'.format( formLogin.email.data, formLogin.password.data, formLogin.remember.data ))
    if(formRegister.validate_on_submit()):
        print(formRegister.name.data, formRegister.email.data, formRegister.password.data, formRegister.confirmPassword.data)
    title='Inicio'
    route = '/ Inicio'
    return render_template('inicio.html', title=title, route=route, formLogin=formLogin,formRegister=formRegister )

@app.route('/welcome')
def welcome():
    title='Bienvenida'
    route = '/ Bienvenida'
    return render_template('bienvenida.html', title=title, route=route)

@app.route('/newMessage')
def newMessage():
    title = 'Mensaje nuevo'
    route = '/ Mensaje nuevo'
    return render_template('newMessage.html', title=title, route=route)
    #params = request.args.get('nombre_param', 'valor_por_defecto')   
    #return 'El parametro es {}'.format(params) 

@app.route('/messages')
def messages():
    title = 'Bandeja de entrada'
    route = '/ Bandeja de entrada'
    return render_template('messages.html', title=title, route=route)


if __name__ == '__main__':    
    app.run(debug=True)