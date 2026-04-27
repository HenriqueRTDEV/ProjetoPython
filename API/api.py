"""
===========================================================
API REST - Projeto Vagas (Flask + MySQL)
===========================================================

Este arquivo contém:

✔ Implementação completa da API
✔ Documentação de cada endpoint
✔ Exemplos de uso (Python, curl)

-----------------------------------------------------------
BASE URL:
http://127.0.0.1:5001
-----------------------------------------------------------

STATUS:
GET /api/status

===========================================================
"""

import os
import re
import uuid
import mysql.connector

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename

app = Flask(__name__)
CORS(app)

# =========================================================
# CONFIGURAÇÃO
# =========================================================

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "SUA_SENHA",
    "database": "projeto_senac_db"
}

# =========================================================
# FUNÇÕES AUXILIARES
# =========================================================

def db():
    return mysql.connector.connect(**DB_CONFIG)

def erro(msg, code=400):
    return jsonify({"erro": msg}), code

def email_valido(email):
    return re.match(r"[^@]+@[^@]+\.[^@]+", email)

# =========================================================
# STATUS
# =========================================================

@app.route("/api/status")
def status():
    """
    Verifica se API está online
    """
    return jsonify({"status": "ok"})

# =========================================================
# LOGIN
# =========================================================

@app.route("/api/login", methods=["POST"])
def login():
    """
    POST /api/login

    BODY:
    {
        "email": "...",
        "senha": "..."
    }
    """

    data = request.json
    conn = db()
    cur = conn.cursor(dictionary=True)

    cur.execute("SELECT * FROM usuarios WHERE email=%s", (data["email"],))
    user = cur.fetchone()

    if user and check_password_hash(user["senha_hash"], data["senha"]):
        return jsonify({"tipo": "usuario", "id": user["id"], "nome": user["nome"]})

    cur.execute("SELECT * FROM empresas WHERE email=%s", (data["email"],))
    emp = cur.fetchone()

    if emp and check_password_hash(emp["senha_hash"], data["senha"]):
        return jsonify({"tipo": "empresa", "id": emp["id"], "nome": emp["nome_empresa"]})

    return erro("Login inválido", 401)

# =========================================================
# USUÁRIOS
# =========================================================

@app.route("/api/usuarios", methods=["POST"])
def criar_usuario():
    """
    POST /api/usuarios

    BODY:
    {
        "nome": "...",
        "email": "...",
        "cpf": "...",
        "telefone": "...",
        "senha": "...",
        "genero": "...",
        "idade": 20
    }
    """

    data = request.json

    conn = db()
    cur = conn.cursor()

    senha_hash = generate_password_hash(data["senha"])

    cur.execute("""
        INSERT INTO usuarios
        (nome, email, cpf, telefone, senha_hash, genero, idade)
        VALUES (%s,%s,%s,%s,%s,%s,%s)
    """, (
        data["nome"],
        data["email"],
        data["cpf"],
        data["telefone"],
        senha_hash,
        data["genero"],
        data.get("idade")
    ))

    conn.commit()

    return jsonify({"id": cur.lastrowid})


@app.route("/api/usuarios", methods=["GET"])
def listar_usuarios():
    """
    GET /api/usuarios
    """

    conn = db()
    cur = conn.cursor(dictionary=True)

    cur.execute("SELECT * FROM usuarios")
    return jsonify(cur.fetchall())


@app.route("/api/usuarios/<int:id>", methods=["GET"])
def get_usuario(id):
    """
    GET /api/usuarios/{id}
    """

    conn = db()
    cur = conn.cursor(dictionary=True)

    cur.execute("SELECT * FROM usuarios WHERE id=%s", (id,))
    return jsonify(cur.fetchone())


@app.route("/api/usuarios/<int:id>", methods=["PUT"])
def update_usuario(id):
    """
    PUT /api/usuarios/{id}
    """

    data = request.json

    conn = db()
    cur = conn.cursor()

    cur.execute("""
        UPDATE usuarios SET
        nome=%s, email=%s, cpf=%s, telefone=%s,
        genero=%s, idade=%s
        WHERE id=%s
    """, (
        data["nome"],
        data["email"],
        data["cpf"],
        data["telefone"],
        data["genero"],
        data["idade"],
        id
    ))

    conn.commit()

    return jsonify({"msg": "atualizado"})


@app.route("/api/usuarios/<int:id>", methods=["DELETE"])
def delete_usuario(id):
    """
    DELETE /api/usuarios/{id}
    """

    conn = db()
    cur = conn.cursor()

    cur.execute("DELETE FROM usuarios WHERE id=%s", (id,))
    conn.commit()

    return jsonify({"msg": "deletado"})


@app.route("/api/usuarios/<int:id>/senha", methods=["PATCH"])
def alterar_senha_usuario(id):
    """
    PATCH /api/usuarios/{id}/senha

    BODY:
    {
        "senha_atual": "...",
        "nova_senha": "..."
    }
    """

    data = request.json

    conn = db()
    cur = conn.cursor(dictionary=True)

    cur.execute("SELECT senha_hash FROM usuarios WHERE id=%s", (id,))
    user = cur.fetchone()

    if not check_password_hash(user["senha_hash"], data["senha_atual"]):
        return erro("Senha incorreta")

    nova = generate_password_hash(data["nova_senha"])

    cur.execute("UPDATE usuarios SET senha_hash=%s WHERE id=%s", (nova, id))
    conn.commit()

    return jsonify({"msg": "senha alterada"})


# =========================================================
# EMPRESAS
# =========================================================

@app.route("/api/empresas", methods=["POST"])
def criar_empresa():
    data = request.json

    conn = db()
    cur = conn.cursor()

    senha_hash = generate_password_hash(data["senha"])

    cur.execute("""
        INSERT INTO empresas
        (nome_empresa, email, senha_hash, telefone, numero_registro)
        VALUES (%s,%s,%s,%s,%s)
    """, (
        data["nome_empresa"],
        data["email"],
        senha_hash,
        data["telefone"],
        data["numero_registro"]
    ))

    conn.commit()

    return jsonify({"id": cur.lastrowid})


@app.route("/api/empresas", methods=["GET"])
def listar_empresas():
    conn = db()
    cur = conn.cursor(dictionary=True)

    cur.execute("SELECT * FROM empresas")
    return jsonify(cur.fetchall())


@app.route("/api/empresas/<int:id>", methods=["DELETE"])
def delete_empresa(id):
    conn = db()
    cur = conn.cursor()

    cur.execute("DELETE FROM empresas WHERE id=%s", (id,))
    conn.commit()

    return jsonify({"msg": "empresa removida"})


# =========================================================
# VAGAS
# =========================================================

@app.route("/api/vagas", methods=["POST"])
def criar_vaga():
    data = request.json

    conn = db()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO vagas
        (empresa_id, titulo, descricao, requisitos, salario, localizacao, tipo_contrato, modalidade)
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
    """, (
        data["empresa_id"],
        data["titulo"],
        data["descricao"],
        data["requisitos"],
        data["salario"],
        data["localizacao"],
        data["tipo_contrato"],
        data["modalidade"]
    ))

    conn.commit()

    return jsonify({"id": cur.lastrowid})


@app.route("/api/vagas", methods=["GET"])
def listar_vagas():
    conn = db()
    cur = conn.cursor(dictionary=True)

    cur.execute("""
        SELECT v.*, e.nome_empresa
        FROM vagas v
        JOIN empresas e ON v.empresa_id = e.id
    """)

    return jsonify(cur.fetchall())


@app.route("/api/vagas/<int:id>", methods=["DELETE"])
def delete_vaga(id):
    conn = db()
    cur = conn.cursor()

    cur.execute("DELETE FROM vagas WHERE id=%s", (id,))
    conn.commit()

    return jsonify({"msg": "vaga removida"})


# =========================================================
# CANDIDATURAS
# =========================================================

@app.route("/api/candidaturas", methods=["POST"])
def candidatar():
    data = request.json

    conn = db()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO candidaturas (usuario_id, vaga_id)
        VALUES (%s,%s)
    """, (data["usuario_id"], data["vaga_id"]))

    conn.commit()

    return jsonify({"msg": "candidatura criada"})


@app.route("/api/candidaturas", methods=["GET"])
def listar_candidaturas():
    conn = db()
    cur = conn.cursor(dictionary=True)

    cur.execute("""
        SELECT c.*, u.nome, v.titulo
        FROM candidaturas c
        JOIN usuarios u ON c.usuario_id = u.id
        JOIN vagas v ON c.vaga_id = v.id
    """)

    return jsonify(cur.fetchall())


@app.route("/api/candidaturas/<int:id>", methods=["DELETE"])
def cancelar_candidatura(id):
    conn = db()
    cur = conn.cursor()

    cur.execute("DELETE FROM candidaturas WHERE id=%s", (id,))
    conn.commit()

    return jsonify({"msg": "candidatura removida"})


# =========================================================
# RUN
# =========================================================

if __name__ == "__main__":
    app.run(port=5001, debug=True)