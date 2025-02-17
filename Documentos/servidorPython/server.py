import os
import sqlite3
import RPi.GPIO as GPIO
from flask import Flask, request, render_template_string, redirect, url_for
from werkzeug.security import generate_password_hash, check_password_hash
import time

app = Flask(__name__)

# Configuração do GPIO para o servo motor
GPIO.setmode(GPIO.BCM)
servo_pin = 18  # O pino do GPIO que controlará o servo motor
GPIO.setup(servo_pin, GPIO.OUT)
pwm = GPIO.PWM(servo_pin, 50)  # PWM na frequência de 50Hz
pwm.start(0)  # Inicia o PWM com o ciclo de trabalho em 0%

# Excluir o arquivo do banco de dados, se ele existir
if os.path.exists('usuarios.db'):
    os.remove('usuarios.db')

# Função para conectar ao banco de dados SQLite
def get_db_connection():
    conn = sqlite3.connect('usuarios.db')
    conn.row_factory = sqlite3.Row
    return conn

# Criação da tabela no banco de dados (executar apenas uma vez)
def create_table():
    conn = get_db_connection()
    conn.execute('''CREATE TABLE IF NOT EXISTS usuarios (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        senha TEXT NOT NULL
                    );''')
    conn.commit()
    conn.close()

# Função para mover o servo motor
def abrir_fechadura():
    pwm.ChangeDutyCycle(7)  # Ajuste para a posição de "abertura"
    time.sleep(1)  # Aguarda 1 segundo para a ação
    pwm.ChangeDutyCycle(0)  # Desliga o PWM para o servo motor

# Página de login
@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        senha = request.form['senha']
        
        conn = get_db_connection()
        user = conn.execute('SELECT * FROM usuarios WHERE id = 1').fetchone()
        conn.close()
        
        if user and check_password_hash(user['senha'], senha):
            return redirect(url_for('sucesso'))
        else:
            return render_template_string(error_page())

    return render_template_string(login_page())

# Página de cadastro
@app.route('/cadastro', methods=['GET', 'POST'])
def cadastro():
    if request.method == 'POST':
        senha = request.form['senha']
        senha_hash = generate_password_hash(senha)

        conn = get_db_connection()
        conn.execute('INSERT INTO usuarios (senha) VALUES (?)', (senha_hash,))
        conn.commit()
        conn.close()
        return redirect(url_for('login'))

    return render_template_string(cadastro_page())

# Página de sucesso
@app.route('/sucesso')
def sucesso():
    return render_template_string(sucesso_page())

# Página para abrir a fechadura
@app.route('/fechadura', methods=['GET', 'POST'])
def fechadura():
    if request.method == 'POST':
        abrir_fechadura()  # Ativa o servo motor para abrir a fechadura
        return render_template_string(sucesso_page())  # Retorna para a página de sucesso após abrir a fechadura

    return render_template_string(fechadura_page())

# Página de erro
def error_page():
    return '''
    <!DOCTYPE html>
    <html lang="pt-br">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Erro</title>
        <style>
            body { font-family: Arial, sans-serif; background-color: #f4f4f9; display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; }
            .container { background-color: #fff; padding: 30px; border-radius: 10px; box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1); text-align: center; }
            h1 { color: #f44336; }
            p { color: #333; font-size: 18px; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Senha Incorreta!</h1>
            <p>Por favor, tente novamente.</p>
        </div>
    </body>
    </html>
    '''

# Página de sucesso
def sucesso_page():
    return '''
    <!DOCTYPE html>
    <html lang="pt-br">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Sucesso</title>
        <style>
            body { font-family: Arial, sans-serif; background-color: #f4f4f9; display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; }
            .container { background-color: #fff; padding: 30px; border-radius: 10px; box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1); text-align: center; }
            h1 { color: #4CAF50; }
            p { color: #333; font-size: 18px; }
            a { color: #4CAF50; font-size: 16px; text-decoration: none; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Login Bem-Sucedido!</h1>
            <p>Acesso concedido. Agora você pode abrir a fechadura.</p>
            <a href="/fechadura">Abrir Fechadura</a>
        </div>
    </body>
    </html>
    '''

# Página de cadastro
def cadastro_page():
    return '''
    <!DOCTYPE html>
    <html lang="pt-br">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Cadastro</title>
        <style>
            body { font-family: Arial, sans-serif; background-color: #f4f4f9; display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; }
            .container { background-color: #fff; padding: 30px; border-radius: 10px; box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1); width: 300px; text-align: center; }
            h1 { color: #333; }
            input[type="password"] { width: 100%; padding: 10px; margin: 10px 0; border: 1px solid #ddd; border-radius: 5px; font-size: 16px; }
            button { width: 100%; padding: 10px; background-color: #4CAF50; color: white; border: none; border-radius: 5px; font-size: 16px; cursor: pointer; }
            button:hover { background-color: #45a049; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Cadastro</h1>
            <form method="POST">
                <input type="password" name="senha" placeholder="Digite a senha" required>
                <button type="submit">Cadastrar</button>
            </form>
        </div>
    </body>
    </html>
    '''

# Página de login
def login_page():
    return '''
    <!DOCTYPE html>
    <html lang="pt-br">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Login</title>
        <style>
            body { font-family: Arial, sans-serif; background-color: #f4f4f9; display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; }
            .container { background-color: #fff; padding: 30px; border-radius: 10px; box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1); width: 300px; text-align: center; }
            h1 { color: #333; }
            input[type="password"] { width: 100%; padding: 10px; margin: 10px 0; border: 1px solid #ddd; border-radius: 5px; font-size: 16px; }
            button { width: 100%; padding: 10px; background-color: #4CAF50; color: white; border: none; border-radius: 5px; font-size: 16px; cursor: pointer; }
            button:hover { background-color: #45a049; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Login</h1>
            <form method="POST">
                <input type="password" name="senha" placeholder="Digite a senha" required>
                <button type="submit">Entrar</button>
            </form>
            <p><a href="/cadastro">Cadastrar-se</a></p>
        </div>
    </body>
    </html>
    '''

# Página para abrir fechadura
def fechadura_page():
    return '''
    <!DOCTYPE html>
    <html lang="pt-br">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Abrir Fechadura</title>
        <style>
            body { font-family: Arial, sans-serif; background-color: #f4f4f9; display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; }
            .container { background-color: #fff; padding: 30px; border-radius: 10px; box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1); text-align: center; }
            h1 { color: #333; }
            button { width: 100%; padding: 10px; background-color: #4CAF50; color: white; border: none; border-radius: 5px; font-size: 16px; cursor: pointer; }
            button:hover { background-color: #45a049; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Abrir Fechadura</h1>
            <form method="POST">
                <button type="submit">Abrir Fechadura</button>
            </form>
        </div>
    </body>
    </html>
    '''

# Função que cria a tabela no banco ao iniciar o app
create_table()

if __name__ == "__main__":
    try:
        app.run(debug=True)
    except KeyboardInterrupt:
        GPIO.cleanup()  # Limpeza do GPIO quando o app é interrompido


