from flask import Blueprint, render_template, request, redirect, url_for, jsonify, flash
from flask_login import login_user, login_required, logout_user, current_user
from .models import User
from . import db, login_manager
from .services import FilterData, get_flight_data
from datetime import datetime
from sqlalchemy import create_engine 
import pandas as pd
import logging

bp = Blueprint('main', __name__)
logger = logging.getLogger(__name__)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Redirecionando para o login
@bp.route('/')
def index():
    return redirect(url_for('main.login'))

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            login_user(user)
            flash('Login realizado com sucesso!', 'success')
            return redirect(url_for('main.dashboard'))
        flash('Usuário ou senha inválidos.', 'danger')
    return render_template('login.html')

@bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if len(username) < 3 or len(password) < 6:
            flash('Usuário (mín. 3) ou senha (mín. 6) inválidos.', 'danger')
            return redirect(url_for('main.register'))
        if User.query.filter_by(username=username).first():
            flash('Usuário já existe.', 'danger')
            return redirect(url_for('main.register'))

        user = User(username=username, password=password)
        db.session.add(user)
        db.session.commit()
        flash('Registrado com sucesso! Faça login.', 'success')
        return redirect(url_for('main.login'))
    return render_template('register.html')

@bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logout realizado com sucesso!', 'success')
    return redirect(url_for('main.login'))

@bp.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    engine = create_engine('sqlite:///flight_stats.db')
    df = pd.read_sql('SELECT * FROM flight_data', con=engine)
    mercados = sorted(df['MERCADO'].unique().tolist())
    anos = sorted(df['ANO'].unique().tolist())
    current_year, current_month = datetime.now().year, datetime.now().month

    if request.method == 'POST':
        try:
            filter_data = FilterData(
                mercado=request.form['mercado'],
                ano_inicio=int(request.form['ano_inicio']),
                ano_fim=int(request.form['ano_fim']),
                mes_inicio=int(request.form.get('mes_inicio', 1)),
                mes_fim=int(request.form.get('mes_fim', 12))
            )
            chart_data = get_flight_data(filter_data)
            return jsonify(chart_data)
        except ValueError as e:
            logger.error(f"Erro de validação: {str(e)}")
            return jsonify({'error': str(e)}), 400
        except Exception as e:
            logger.error(f"Erro interno: {str(e)}")
            return jsonify({'error': 'Erro interno no servidor.'}), 500

    return render_template('dashboard.html', mercados=mercados, anos=anos,
                         current_year=current_year, current_month=current_month)