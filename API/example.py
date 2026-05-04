"""
===========================================================
EXEMPLOS DE USO DA API REST (Python)
===========================================================

BASE URL:
http://127.0.0.1:5001

Biblioteca usada:
requests

Instalação:
pip install requests
===========================================================
"""

import requests

BASE_URL = "http://127.0.0.1:5001"


# =========================================================
# STATUS
# =========================================================

# Verificar se API está online
response = requests.get(f"{BASE_URL}/api/status")
print(response.json())


# =========================================================
# USUÁRIOS
# =========================================================

# Criar usuário
response = requests.post(f"{BASE_URL}/api/usuarios", json={
    "nome": "João",
    "email": "joao@email.com",
    "cpf": "12345678901",
    "telefone": "55999999999",
    "senha": "123456",
    "genero": "masculino",
    "idade": 25
})
print(response.json())


# Listar usuários
response = requests.get(f"{BASE_URL}/api/usuarios")
print(response.json())


# Buscar usuário por ID
response = requests.get(f"{BASE_URL}/api/usuarios/1")
print(response.json())


# Atualizar usuário
response = requests.put(f"{BASE_URL}/api/usuarios/1", json={
    "nome": "João Atualizado",
    "email": "joao@email.com",
    "cpf": "12345678901",
    "telefone": "55988888888",
    "genero": "masculino",
    "idade": 30
})
print(response.json())


# Alterar senha
response = requests.patch(f"{BASE_URL}/api/usuarios/1/senha", json={
    "senha_atual": "123456",
    "nova_senha": "654321"
})
print(response.json())


# Excluir usuário
response = requests.delete(f"{BASE_URL}/api/usuarios/1")
print(response.json())


# =========================================================
# EMPRESAS
# =========================================================

# Criar empresa
response = requests.post(f"{BASE_URL}/api/empresas", json={
    "nome_empresa": "Empresa X",
    "email": "empresa@email.com",
    "senha": "123456",
    "telefone": "55999999999",
    "numero_registro": "12345678000199"
})
print(response.json())


# Listar empresas
response = requests.get(f"{BASE_URL}/api/empresas")
print(response.json())


# Buscar empresa por ID
response = requests.get(f"{BASE_URL}/api/empresas/1")
print(response.json())


# Excluir empresa
response = requests.delete(f"{BASE_URL}/api/empresas/1")
print(response.json())


# =========================================================
# LOGIN
# =========================================================

# Login usuário ou empresa
response = requests.post(f"{BASE_URL}/api/login", json={
    "email": "joao@email.com",
    "senha": "654321"
})
print(response.json())


# =========================================================
# VAGAS
# =========================================================

# Criar vaga
response = requests.post(f"{BASE_URL}/api/vagas", json={
    "empresa_id": 1,
    "titulo": "Estágio TI",
    "descricao": "Suporte técnico",
    "requisitos": "Conhecimento básico",
    "salario": "R$1000",
    "localizacao": "Remoto",
    "tipo_contrato": "Estágio",
    "modalidade": "Remoto"
})
print(response.json())


# Listar vagas
response = requests.get(f"{BASE_URL}/api/vagas")
print(response.json())


# Buscar vaga por ID
response = requests.get(f"{BASE_URL}/api/vagas/1")
print(response.json())


# Excluir vaga
response = requests.delete(f"{BASE_URL}/api/vagas/1")
print(response.json())


# =========================================================
# CANDIDATURAS
# =========================================================

# Criar candidatura
response = requests.post(f"{BASE_URL}/api/candidaturas", json={
    "usuario_id": 1,
    "vaga_id": 1
})
print(response.json())


# Listar candidaturas
response = requests.get(f"{BASE_URL}/api/candidaturas")
print(response.json())


# Cancelar candidatura
response = requests.delete(f"{BASE_URL}/api/candidaturas/1")
print(response.json())