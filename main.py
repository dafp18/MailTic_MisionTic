from flask import Flask,request,render_template,flash
import os
SECRET_KEY = os.urandom(32)
import forms
import utils

app = Flask(__name__)
app.config['SECRET_KEY'] = SECRET_KEY

@app.route('/', methods=['GET','POST'])
def index():
    colorAlert = "alert-danger"
    title='Inicio'
    route = '/ Inicio'
    formLogin = forms.LoginForm()
    formRegister = forms.RegisterForm()
    if(formLogin.validate_on_submit() and request.method == 'POST'):
        email = formLogin.email.data
        password = formLogin.password.data
        remember = formLogin.remember.data
        flash('usuario {}, password {}, recordar {}'.format( email, password, remember ))
        pass
    if(formRegister.validate_on_submit() and request.method == 'POST'):
        try:
            name = formRegister.name.data
            email = formRegister.email.data
            password = formRegister.password.data
            confirmPassword = formRegister.confirmPassword.data
            error = None
        
            if not utils.isUsernameValid(name):
                error = "el usuario debe ser alfanumerico o incluir solo '.',  '_', '-' "
                flash(error)
                
            
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
                flash('Cuenta creada correctamente revisa tu correo para activarla.')
                return render_template('inicio.html', title=title, route=route, formLogin=formLogin,formRegister=formRegister,colorAlert=colorAlert )
        except:
            return render_template('inicio.html', title=title, route=route, formLogin=formLogin,formRegister=formRegister,colorAlert=colorAlert )
    return render_template('inicio.html', title=title, route=route, formLogin=formLogin,formRegister=formRegister,colorAlert=colorAlert )    
    

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