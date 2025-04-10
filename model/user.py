from sqlalchemy import Column, String, Integer
from model import Base
import re

class User(Base):
    __tablename__ = 'users'

    id = Column("pk_user", Integer, primary_key=True)
    cpf = Column(String(11), nullable=False, unique=True)
    password = Column(String(18), nullable=False)
    user_type = Column(String(20), nullable=False)

    def __init__(self, cpf: str, password: str, user_type: str):
        if not self.validate_cpf(cpf):
            raise ValueError("CPF inválido")
        if not self.validate_password(password):
            raise ValueError("Senha inválida: deve conter pelo menos 1 letra maiúscula, 1 letra minúscula, 1 número e ter no mínimo 6 caracteres.")
        
        self.cpf = cpf
        self.password = password
        self.user_type = user_type

    @staticmethod
    def validate_cpf(cpf: str) -> bool:
        """Valida um CPF conforme o algoritmo oficial"""
        cpf = re.sub(r'[^0-9]', '', cpf)  # Remove caracteres não numéricos
        if len(cpf) != 11 or cpf in ("00000000000", "11111111111", "22222222222", "33333333333", "44444444444", "55555555555", "66666666666", "77777777777", "88888888888", "99999999999"):
            return False
        
        def calculate_digit(cpf, length):
            sum_values = sum(int(cpf[i]) * (length - i) for i in range(length - 1))
            remainder = (sum_values * 10) % 11
            return 0 if remainder == 10 else remainder
        
        return calculate_digit(cpf, 10) == int(cpf[9]) and calculate_digit(cpf, 11) == int(cpf[10])

    @staticmethod
    def validate_password(password: str) -> bool:
        """Valida se a senha atende aos requisitos:
            1 caractere maísculo
            1 caractere minusculo
            1 número
            mínimo de 6 caracteres 
        """
        return (
            len(password) >= 6 and
            re.search(r'[A-Z]', password) and
            re.search(r'[a-z]', password) and
            re.search(r'[0-9]', password)
        )
