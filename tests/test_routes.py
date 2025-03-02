import pytest
from flask import url_for
from app import create_app, db
from app.models import User
from pytest_mock import MockerFixture

@pytest.fixture
def client():
    """Cria um cliente de teste Flask."""
    app = create_app()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            yield client
        with app.app_context():
            db.drop_all()

def test_login_get(client):
    """Testa a rota GET /login."""
    response = client.get('/login')
    assert response.status_code == 200
    assert b'Login' in response.data

def test_login_post_success(client, mocker):
    """Testa login bem-sucedido."""
    mocker.patch('app.models.User.check_password', return_value=True)
    user = User(username='testuser', password='testpass')
    db.session.add(user)
    db.session.commit()
    response = client.post('/login', data={'username': 'testuser', 'password': 'testpass'})
    assert response.status_code == 302 
    assert response.headers['Location'] == '/dashboard'

def test_dashboard_get(client, mocker):
    """Testa a rota GET /dashboard com usuário logado."""
    mocker.patch('flask_login.utils._get_user', return_value=User(username='testuser', password='testpass'))
    mocker.patch('app.services.get_dashboard_initial_data', return_value={
        'mercados': ['SBGRSBSV'],
        'anos': [2023]
    })
    response = client.get('/dashboard')
    assert response.status_code == 200
    assert 'Estatísticas de Voos GOL'.encode('utf-8') in response.data
