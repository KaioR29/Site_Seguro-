import os
import random
import sqlite3
import smtplib
import uuid
from datetime import datetime
from email.mime.text import MIMEText

from flask import (
    Flask, render_template, request, redirect,
    url_for, session, flash, jsonify
)
from werkzeug.security import generate_password_hash, check_password_hash

from models import User, DataRequest
from env_email import env_email

app = Flask(__name__, static_url_path='', static_folder='static')
app.secret_key = os.getenv("SECRET_KEY", "chave_secreta_super_segura")

@app.context_processor
def inject_request():
    return dict(request=request)

def get_db_connection():
    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row
    return conn

def send_verification_email(email, verification_code):
    mensagem = f'Seu código de verificação é: {verification_code}'
    assunto = 'Código de Verificação'
    return env_email(email, assunto, mensagem)

@app.before_request
def log_request():
    if 'user_id' in session:
        User.log_access(
            user_id=session['user_id'],
            action=f"{request.method} {request.path}",
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent')
        )

@app.route('/')
def home():
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['senha']

        if 'lgpd_consent' not in request.form:
            flash('Você deve concordar com nossa Política de Privacidade para se registrar', 'error')
            return redirect(url_for('register'))

        try:
            new_user = User(username, email, password)
            user_id = new_user.save()

            verification_code = str(random.randint(100000, 999999))
            send_verification_email(email, verification_code)

            session.update({
                'verification_code': verification_code,
                'user_id_temp': user_id,
                'username_temp': username,
                'email': email
            })

            flash('Cadastro realizado com sucesso! Verifique seu e-mail para o código de verificação.', 'success')
            return redirect(url_for('verificar', email=email))
        except ValueError as e:
            flash(str(e), 'error')

    return render_template('cadastro.html')

@app.route('/verificar', methods=['GET', 'POST'])
def verificar():
    if request.method == 'POST':
        if request.form['codigo'] == session.get('verification_code'):
            user_id = session.pop('user_id_temp', None)
            username = session.pop('username_temp', None)
            session.pop('verification_code', None)

            if user_id:
                user = User.get_by_id(user_id)
                if user and not user.is_verified:
                    user.set_verified(user_id)

            session.update({
                'user_id': user_id,
                'username': username
            })

            flash('Verificação realizada com sucesso!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Código de verificação inválido. Tente novamente.', 'error')

    return render_template('verificar.html', email=session.get('email'))

from datetime import timedelta, datetime

@app.route('/login', methods=['GET', 'POST'])
def login():
    MAX_ATTEMPTS = 5
    BLOCK_TIME = timedelta(seconds=10)

    if 'login_attempts' not in session:
        session['login_attempts'] = 0
    if 'block_until' in session:
        block_until = session['block_until']
        if block_until:
            block_until_dt = datetime.strptime(block_until, '%Y-%m-%d %H:%M:%S.%f')
            if datetime.now() < block_until_dt:
                remaining = (block_until_dt - datetime.now()).seconds // 60 + 1
                flash(f'Tentativas de login excedidas. Tente novamente em {remaining} segundos.', 'error')
                return render_template('login.html')
            else:
                session.pop('block_until', None)
                session['login_attempts'] = 0

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        try:
            user, user_id = User.get_by_username(username)
            if user and user.check_password(password):
                if not user.is_verified:
                    verification_code = str(random.randint(100000, 999999))
                    send_verification_email(user.email, verification_code)
                    session.update({
                        'verification_code': verification_code,
                        'user_id_temp': user_id,
                        'username_temp': username,
                        'email': user.email
                    })
                    flash('Por favor, verifique seu e-mail antes de fazer login.', 'error')
                    return redirect(url_for('verificar'))

                session.update({
                    'user_id': user_id,
                    'username': username
                })
                session['login_attempts'] = 0  # resetar contador após sucesso

                flash('Login realizado com sucesso!', 'success')
                return redirect(url_for('dashboard'))
            else:
                session['login_attempts'] += 1
                if session['login_attempts'] >= MAX_ATTEMPTS:
                    block_until_dt = datetime.now() + BLOCK_TIME
                    session['block_until'] = str(block_until_dt)
                    flash(f'Tentativas de login excedidas. Tente novamente em {BLOCK_TIME.seconds // 60} minutos.', 'error')
                else:
                    flash('Usuário ou senha incorretos', 'error')
        except ValueError:
            session['login_attempts'] += 1
            if session['login_attempts'] >= MAX_ATTEMPTS:
                block_until_dt = datetime.now() + BLOCK_TIME
                session['block_until'] = str(block_until_dt)
                flash(f'Tentativas de login excedidas. Tente novamente em {BLOCK_TIME.seconds // 60} minutos.', 'error')
            else:
                flash('Usuário não encontrado', 'error')

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('Você foi desconectado com sucesso', 'info')
    return redirect(url_for('login'))

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('dashboard.html', username=session.get('username'))

@app.route('/privacy')
def privacy():
    return render_template('privacy.html')

@app.route('/request-data', methods=['POST'])
def request_data():
    if 'user_id' not in session:
        return jsonify({'error': 'Não autenticado'}), 401

    request_type = request.json.get('type')
    if request_type not in ['access', 'rectification', 'deletion', 'portability']:
        return jsonify({'error': 'Tipo de solicitação inválido'}), 400

    DataRequest.create_request(session['user_id'], request_type)
    return jsonify({'success': True})

@app.route('/my-requests')
def my_requests():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    requests = DataRequest.get_user_requests(session['user_id'])
    return render_template('my_requests.html', requests=requests)

if __name__ == '__main__':
    from database import init_db
    init_db()
    app.run(debug=True)
