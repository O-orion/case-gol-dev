from . import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from pydantic import BaseModel, validator
from flask_sqlalchemy import SQLAlchemy;
from typing import Optional


class User(db.Model, UserMixin):
    """Modelo de usuário para autenticação."""
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)

    def __init__(self, username: str, password: str):
        self.username = username
        self.password = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password, password)

    def __repr__(self) -> str:
        return f'<User {self.username}>'

class FilterData(BaseModel):
    """Modelo de dados para filtros do dashboard."""
    mercado: str
    ano_inicio: int
    ano_fim: int
    mes_inicio: int = 1
    mes_fim: int = 12

    @validator('ano_fim')
    def ano_fim_maior_que_inicio(cls, v: int, values: dict) -> int:
        if 'ano_inicio' in values and v < values['ano_inicio']:
            raise ValueError('Ano fim deve ser maior ou igual ao ano início.')
        return v

    @validator('mes_fim')
    def mes_fim_valido(cls, v: int, values: dict) -> int:
        if 'mes_inicio' in values and 'ano_inicio' in values and 'ano_fim' in values:
            if values['ano_inicio'] == values['ano_fim'] and v < values['mes_inicio']:
                raise ValueError('Mês fim deve ser maior ou igual ao mês início no mesmo ano.')
        return v
    
class UserFilter(db.Model):
    """Modelo para armazenar filtros usados por usuários."""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    mercado = db.Column(db.String(20), nullable=False)
    ano_inicio = db.Column(db.Integer, nullable=False)
    ano_fim = db.Column(db.Integer, nullable=False)
    mes_inicio = db.Column(db.Integer, nullable=False)
    mes_fim = db.Column(db.Integer, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self) -> str:
        return f'<UserFilter {self.user_id} - {self.mercado} {self.ano_inicio}-{self.mes_inicio} to {self.ano_fim}-{self.mes_fim}>'