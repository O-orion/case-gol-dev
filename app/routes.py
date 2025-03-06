from flask import Blueprint, render_template, request, redirect, url_for, jsonify, flash, Response
from flask_login import login_user, login_required, logout_user, current_user
from . import db, login_manager
from .models import User, FilterData, UserFilter
from .services import get_flight_data, get_flight_RPK, get_flight_data_csv, get_dashboard_initial_data, FlightDataRepository, get_flight_data_pdf
from datetime import datetime
import logging

bp = Blueprint('main', __name__)
logger = logging.getLogger(__name__)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

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
        try:
            user = User(username=username, password=password)
            db.session.add(user)
            db.session.commit()
            logger.info(f"Usuário {username} registrado com sucesso")
            flash('Registrado com sucesso! Faça login.', 'success')
            return redirect(url_for('main.login'))
        except Exception as e:
            logger.error(f"Erro ao registrar usuário: {str(e)}")
            return "Internal Server Error", 500
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
    """
    Exibe o dashboard com filtros, gráfico de RPK e histórico de consultas.

    Returns:
        Para GET: Renderiza o template do dashboard.
        Para POST: Retorna JSON com dados do gráfico.
    """
    repo = FlightDataRepository()
    initial_data = get_dashboard_initial_data(repo)
    mercados = initial_data['mercados']
    anos = initial_data['anos']
    current_year, current_month = datetime.now().year, datetime.now().month

    # Pega histórico de consultas do usuário e formata os meses
    history = UserFilter.query.filter_by(user_id=current_user.id).order_by(UserFilter.timestamp.desc()).limit(5).all()
    history_formatted = [
        {
            'mercado': f.mercado,
            'periodo': f"{f.ano_inicio}-{f.mes_inicio:02d} a {f.ano_fim}-{f.mes_fim:02d}",
            'timestamp': f.timestamp.strftime('%d/%m/%Y %H:%M')
        }
        for f in history
    ]

    if request.method == 'POST':
        try:
            filter_data = FilterData(
                mercado=request.form['mercado'],
                ano_inicio=int(request.form['ano_inicio']),
                ano_fim=int(request.form['ano_fim']),
                mes_inicio=int(request.form.get('mes_inicio', 1)),
                mes_fim=int(request.form.get('mes_fim', 12))
            )
            chart_data = get_flight_data(filter_data, repo)
            
            # Salva o filtro no histórico
            user_filter = UserFilter(
                user_id=current_user.id,
                mercado=filter_data.mercado,
                ano_inicio=filter_data.ano_inicio,
                ano_fim=filter_data.ano_fim,
                mes_inicio=filter_data.mes_inicio,
                mes_fim=filter_data.mes_fim
            )
            db.session.add(user_filter)
            db.session.commit()
            logger.info(f"Filtro salvo no histórico para usuário {current_user.id}")

            return jsonify(chart_data)
        except ValueError as e:
            logger.error(f"Erro de validação: {str(e)}")
            return jsonify({'error': str(e)}), 400
        except Exception as e:
            logger.error(f"Erro interno: {str(e)}")
            return jsonify({'error': 'Erro interno no servidor.'}), 500

    return render_template(
        'dashboard.html',
        mercados=mercados,
        anos=anos,
        current_year=current_year,
        current_month=current_month,
        history=history_formatted 
    )

@bp.route('/export_csv', methods=['POST'])
@login_required
def export_csv():
    repo = FlightDataRepository()
    try:
        filter_data = FilterData(
            mercado=request.form['mercado'],
            ano_inicio=int(request.form['ano_inicio']),
            ano_fim=int(request.form['ano_fim']),
            mes_inicio=int(request.form.get('mes_inicio', 1)),
            mes_fim=int(request.form.get('mes_fim', 12))
        )
        csv_content = get_flight_data_csv(filter_data, repo)
        filename = f"rpk_{filter_data.mercado}_{filter_data.ano_inicio}-{filter_data.mes_inicio}_to_{filter_data.ano_fim}-{filter_data.mes_fim}.csv"
        return Response(
            csv_content,
            mimetype="text/csv",
            headers={"Content-Disposition": f"attachment;filename={filename}"}
        )
    except ValueError as e:
        logger.error(f"Erro ao exportar CSV: {str(e)}")
        flash(f"Erro: {str(e)}", 'danger')
        return redirect(url_for('main.dashboard'))
    except Exception as e:
        logger.error(f"Erro interno ao exportar CSV: {str(e)}")
        flash("Erro interno ao gerar o CSV.", 'danger')
        return redirect(url_for('main.dashboard'))

@bp.route('/rpk', methods=['POST'] )
def rpk_quadrado():

    repo = FlightDataRepository()
    initial_data = get_dashboard_initial_data(repo)
    mercados = initial_data['mercados']
    anos = initial_data['anos']
    current_year, current_month = datetime.now().year, datetime.now().month

    logger.info("")
    logger.info("INFOFOFOFOO")
    logger.info("")

    if request.method == 'POST':
        try:
            filter_data = FilterData(
                mercado=request.form['mercado'],
                ano_inicio=int(request.form['ano_inicio']),
                ano_fim=int(request.form['ano_fim']),
                mes_inicio=int(request.form.get('mes_inicio', 1)),
                mes_fim=int(request.form.get('mes_fim', 12))
            )

            logger.info("")
            logger.info(filter_data)
            logger.info("")
            
            chart_data = get_flight_RPK(filter_data, repo)
            
            # Salva o filtro no histórico
            user_filter = UserFilter(
                user_id=current_user.id,
                mercado=filter_data.mercado,
                ano_inicio=filter_data.ano_inicio,
                ano_fim=filter_data.ano_fim,
                mes_inicio=filter_data.mes_inicio,
                mes_fim=filter_data.mes_fim
            )
            db.session.add(user_filter)
            db.session.commit()
            logger.info(f"Filtro salvo no histórico para usuário {current_user.id}")

            return jsonify(chart_data)
        except ValueError as e:
            logger.error(f"Erro de validação: {str(e)}")
            return jsonify({'error': str(e)}), 400
        except Exception as e:
            logger.error(f"Erro interno: {str(e)}")
            return jsonify({'error': 'Erro interno no servidor.'}), 500

    return render_template(
        'dashboard.html',
        mercados=mercados,
        anos=anos,
        current_year=current_year,
        current_month=current_month,
        history=history_formatted 
    )

@bp.route('/export_pdf', methods=['POST'])
@login_required
def export_pdf():
    """Exporta os dados filtrados do dashboard como PDF."""
    repo = FlightDataRepository()
    try:
        filter_data = FilterData(
            mercado=request.form['mercado'],
            ano_inicio=int(request.form['ano_inicio']),
            ano_fim=int(request.form['ano_fim']),
            mes_inicio=int(request.form.get('mes_inicio', 1)),
            mes_fim=int(request.form.get('mes_fim', 12))
        )
        pdf_buffer = get_flight_data_pdf(filter_data, repo)
        if not pdf_buffer:
            flash("Nenhum dado para exportar em PDF.", 'danger')
            return redirect(url_for('main.dashboard'))
        filename = f"rpk_{filter_data.mercado}_{filter_data.ano_inicio}-{filter_data.mes_inicio}_to_{filter_data.ano_fim}-{filter_data.mes_fim}.pdf"
        return Response(
            pdf_buffer,
            mimetype="application/pdf",
            headers={"Content-Disposition": f"attachment;filename={filename}"}
        )
    except ValueError as e:
        logger.error(f"Erro ao exportar PDF: {str(e)}")
        flash(f"Erro: {str(e)}", 'danger')
        return redirect(url_for('main.dashboard'))
    except Exception as e:
        logger.error(f"Erro interno ao exportar PDF: {str(e)}")
        flash("Erro interno ao gerar o PDF.", 'danger')
        return redirect(url_for('main.dashboard'))