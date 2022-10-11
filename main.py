from flask import Flask
from flask import request
from flask import render_template

app = Flask(__name__)
@app.route('/')
def index():
    title='Inicio'
    route = '/ Inicio'
    return render_template('inicio.html', title=title, route=route)

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