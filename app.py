import os
import re
import uuid
import mysql.connector
from mysql.connector import Error
from flask import Flask, render_template, request, redirect, url_for, flash, session, send_from_directory
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = "troque-esta-chave-secreta"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")
ALLOWED_EXTENSIONS = {"pdf"}

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["MAX_CONTENT_LENGTH"] = 5 * 1024 * 1024  # 5MB


#Altere esses campos aqui para seu banco de dados.
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "123456",
    "database": "projeto_senac_db"
}

os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

def get_connection():
    return mysql.connector.connect(**DB_CONFIG)

def validar_email(email):
    return bool(re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", email))

def validar_telefone(telefone):
    numeros = re.sub(r"\D", "", telefone)
    return len(numeros) in (10, 11)

def validar_cnpj(cnpj):
    numeros = re.sub(r"\D", "", cnpj)
    return len(numeros) == 14

def validar_cpf(cpf):
    numeros = re.sub(r"\D", "", cpf)
    return len(numeros) == 11

def somente_numeros(valor):
    return re.sub(r"\D", "", valor or "")

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route("/")
def index():
    return redirect(url_for("login"))

# Cadastro de EMPRESA
# Valida dados (email, senha, telefone, CNPJ)
# Salva empresa no banco
@app.route("/cadastro-empresa", methods=["GET", "POST"])
def cadastro_empresa():
    if request.method == "POST":
        nome_empresa = request.form.get("nome_empresa", "").strip()
        email = request.form.get("email", "").strip().lower()
        senha = request.form.get("senha", "")
        confirmar_senha = request.form.get("confirmar_senha", "")
        telefone = request.form.get("telefone", "").strip()
        numero_registro = request.form.get("numero_registro", "").strip()

        if not nome_empresa:
            flash("Informe o nome da empresa.", "danger")
            return render_template("cadastro-empresa.html")

        if not validar_email(email):
            flash("Email inválido.", "danger")
            return render_template("cadastro-empresa.html")

        if len(senha) < 6:
            flash("A senha deve ter pelo menos 6 caracteres.", "danger")
            return render_template("cadastro-empresa.html")

        if senha != confirmar_senha:
            flash("As senhas não coincidem.", "danger")
            return render_template("cadastro-empresa.html")

        if not validar_telefone(telefone):
            flash("Telefone inválido.", "danger")
            return render_template("cadastro-empresa.html")

        if not validar_cnpj(numero_registro):
            flash("CNPJ inválido.", "danger")
            return render_template("cadastro-empresa.html")

        senha_hash = generate_password_hash(senha)

        conn = None
        cursor = None
        try:
            conn = get_connection()
            cursor = conn.cursor(dictionary=True)

            cursor.execute(
                "SELECT id FROM empresas WHERE email = %s OR numero_registro = %s",
                (email, numero_registro)
            )
            empresa_existente = cursor.fetchone()

            if empresa_existente:
                flash("Já existe uma empresa cadastrada com este email ou CNPJ.", "danger")
                return render_template("cadastro-empresa.html")

            cursor.execute(
                """
                INSERT INTO empresas (nome_empresa, email, senha_hash, telefone, numero_registro)
                VALUES (%s, %s, %s, %s, %s)
                """,
                (nome_empresa, email, senha_hash, telefone, numero_registro)
            )
            conn.commit()

            flash("Empresa cadastrada com sucesso! Faça login para continuar.", "success")
            return redirect(url_for("login"))

        except Error as e:
            flash(f"Erro no banco de dados: {str(e)}", "danger")
            return render_template("cadastro-empresa.html")

        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    return render_template("cadastro-empresa.html")

# Cadastro de USUÁRIO
# Valida dados (email, senha, CPF, telefone)
# Salva usuário no banco
@app.route("/cadastro-usuario", methods=["GET", "POST"])
def cadastro_usuario():
    if request.method == "POST":
        nome = request.form.get("nome", "").strip()
        email = request.form.get("email", "").strip().lower()
        cpf = request.form.get("cpf", "").strip()
        telefone = request.form.get("telefone", "").strip()
        senha = request.form.get("senha", "")
        confirmar_senha = request.form.get("confirmar_senha", "")
        genero = request.form.get("genero", "").strip().lower()

        if not nome:
            flash("Informe o nome do usuário.", "danger")
            return render_template("cadastro-usuario.html")

        if not validar_email(email):
            flash("Email inválido.", "danger")
            return render_template("cadastro-usuario.html")

        if not validar_cpf(cpf):
            flash("CPF inválido.", "danger")
            return render_template("cadastro-usuario.html")

        if not validar_telefone(telefone):
            flash("Telefone inválido.", "danger")
            return render_template("cadastro-usuario.html")

        if len(senha) < 6:
            flash("A senha deve ter pelo menos 6 caracteres.", "danger")
            return render_template("cadastro-usuario.html")

        if senha != confirmar_senha:
            flash("As senhas não coincidem.", "danger")
            return render_template("cadastro-usuario.html")

        if genero not in ["masculino", "feminino"]:
            flash("Selecione um gênero.", "danger")
            return render_template("cadastro-usuario.html")

        senha_hash = generate_password_hash(senha)

        conn = None
        cursor = None
        try:
            conn = get_connection()
            cursor = conn.cursor(dictionary=True)

            cursor.execute(
                "SELECT id FROM usuarios WHERE email = %s OR cpf = %s",
                (email, cpf)
            )
            usuario_existente = cursor.fetchone()

            if usuario_existente:
                flash("Já existe um usuário cadastrado com este email ou CPF.", "danger")
                return render_template("cadastro-usuario.html")

            cursor.execute(
                """
                INSERT INTO usuarios (nome, email, cpf, telefone, senha_hash, genero)
                VALUES (%s, %s, %s, %s, %s, %s)
                """,
                (nome, email, somente_numeros(cpf), telefone, senha_hash, genero)
            )
            conn.commit()

            flash("Usuário cadastrado com sucesso! Faça login para continuar.", "success")
            return redirect(url_for("login"))

        except Error as e:
            flash(f"Erro no banco de dados: {str(e)}", "danger")
            return render_template("cadastro-usuario.html")

        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    return render_template("cadastro-usuario.html")

# LOGIN (usuário ou empresa)
# Verifica credenciais e cria sessão
# Redireciona para o feed
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        senha = request.form.get("password", "")

        if not validar_email(email):
            flash("Informe um email válido.", "danger")
            return render_template("login.html")

        conn = None
        cursor = None
        try:
            conn = get_connection()
            cursor = conn.cursor(dictionary=True)

            cursor.execute("SELECT id, nome, email, senha_hash FROM usuarios WHERE email = %s", (email,))
            usuario = cursor.fetchone()

            if usuario and check_password_hash(usuario["senha_hash"], senha):
                session["usuario_id"] = usuario["id"]
                session["usuario_nome"] = usuario["nome"]
                session["tipo_conta"] = "usuario"
                flash("Login realizado com sucesso!", "success")
                return redirect(url_for("feed"))

            cursor.execute("SELECT id, nome_empresa, email, senha_hash FROM empresas WHERE email = %s", (email,))
            empresa = cursor.fetchone()

            if empresa and check_password_hash(empresa["senha_hash"], senha):
                session["usuario_id"] = empresa["id"]
                session["usuario_nome"] = empresa["nome_empresa"]
                session["tipo_conta"] = "empresa"
                flash("Login realizado com sucesso!", "success")
                return redirect(url_for("feed"))

            flash("Email ou senha incorretos.", "danger")
            return render_template("login.html")

        except Error as e:
            flash(f"Erro no banco de dados: {str(e)}", "danger")
            return render_template("login.html")

        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    return render_template("login.html")

@app.route("/recuperar-senha", methods=["GET", "POST"])
def recuperar_senha():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()

        if not validar_email(email):
            flash("Informe um email válido.", "danger")
            return render_template("recuperar_senha.html")

        conn = None
        cursor = None

        try:
            conn = get_connection()
            cursor = conn.cursor(dictionary=True)

            # verifica usuário
            cursor.execute("SELECT id FROM usuarios WHERE email = %s", (email,))
            usuario = cursor.fetchone()

            # verifica empresa
            cursor.execute("SELECT id FROM empresas WHERE email = %s", (email,))
            empresa = cursor.fetchone()

            if not usuario and not empresa:
                flash("Email não encontrado.", "danger")
                return render_template("recuperar_senha.html")

            # aqui depois você pode mandar email real
            session["email_recuperacao"] = email
            return redirect(url_for("nova_senha"))

        except Error as e:
            flash(f"Erro no banco: {str(e)}", "danger")
            return render_template("recuperar_senha.html")

        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    return render_template("recuperar_senha.html")


@app.route("/nova-senha", methods=["GET", "POST"])
def nova_senha():
    if "email_recuperacao" not in session:
        return redirect(url_for("login"))

    if request.method == "POST":
        nova_senha = request.form.get("senha")

        senha_hash = generate_password_hash(nova_senha)
        email = session["email_recuperacao"]

        conn = get_connection()
        cursor = conn.cursor()

        # atualiza nas duas tabelas
        cursor.execute("UPDATE usuarios SET senha_hash=%s WHERE email=%s", (senha_hash, email))
        cursor.execute("UPDATE empresas SET senha_hash=%s WHERE email=%s", (senha_hash, email))

        conn.commit()

        cursor.close()
        conn.close()

        session.pop("email_recuperacao", None)

        flash("Senha redefinida com sucesso!", "success")
        return redirect(url_for("login"))

    return render_template("nova_senha.html")

# FEED PRINCIPAL (home do sistema)
# Só acessa se estiver logado
@app.route("/feed")
def feed():
    if "usuario_id" not in session:
        flash("Faça login para acessar o sistema.", "warning")
        return redirect(url_for("login"))

    return render_template(
        "feed.html",
        nome=session.get("usuario_nome"),
        tipo=session.get("tipo_conta")
    )

# PERFIL DO USUÁRIO
# Permite editar telefone, idade e enviar PDF (currículo)
# Nome, CPF e email não são editáveis
@app.route("/perfil", methods=["GET", "POST"])
def perfil():
    if "usuario_id" not in session or session.get("tipo_conta") != "usuario":
        flash("Somente usuários podem acessar a tela de perfil.", "warning")
        return redirect(url_for("login"))

    conn = None
    cursor = None

    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        usuario_id = session["usuario_id"]

        if request.method == "POST":
            telefone = request.form.get("telefone", "").strip()
            idade = request.form.get("idade", "").strip()
            curriculo = request.files.get("curriculo_pdf")

            if not validar_telefone(telefone):
                flash("Telefone inválido.", "danger")
                return redirect(url_for("perfil"))

            if not idade.isdigit():
                flash("A idade precisa ser numérica.", "danger")
                return redirect(url_for("perfil"))

            idade_int = int(idade)
            if idade_int < 14 or idade_int > 120:
                flash("Informe uma idade válida.", "danger")
                return redirect(url_for("perfil"))

            pdf_nome_salvo = None

            if curriculo and curriculo.filename:
                if not allowed_file(curriculo.filename):
                    flash("Envie somente arquivo PDF.", "danger")
                    return redirect(url_for("perfil"))

                nome_seguro = secure_filename(curriculo.filename)
                pdf_nome_salvo = f"{uuid.uuid4().hex}_{nome_seguro}"
                caminho_arquivo = os.path.join(app.config["UPLOAD_FOLDER"], pdf_nome_salvo)
                curriculo.save(caminho_arquivo)

            if pdf_nome_salvo:
                cursor.execute(
                    """
                    UPDATE usuarios
                    SET telefone = %s, idade = %s, curriculo_pdf = %s
                    WHERE id = %s
                    """,
                    (telefone, idade_int, pdf_nome_salvo, usuario_id)
                )
            else:
                cursor.execute(
                    """
                    UPDATE usuarios
                    SET telefone = %s, idade = %s
                    WHERE id = %s
                    """,
                    (telefone, idade_int, usuario_id)
                )

            conn.commit()
            flash("Perfil atualizado com sucesso!", "success")
            return redirect(url_for("perfil"))

        cursor.execute(
            """
            SELECT id, nome, cpf, telefone, idade, email, curriculo_pdf
            FROM usuarios
            WHERE id = %s
            """,
            (usuario_id,)
        )
        usuario = cursor.fetchone()

        if not usuario:
            flash("Usuário não encontrado.", "danger")
            return redirect(url_for("logout"))

        return render_template("perfil.html", usuario=usuario)

    except Error as e:
        flash(f"Erro no banco de dados: {str(e)}", "danger")
        return redirect(url_for("feed"))

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

# CADASTRAR NOVA VAGA (somente empresa)
# Valida dados e salva no banco
@app.route("/nova-vaga", methods=["GET", "POST"])
def nova_vaga():
    if "usuario_id" not in session or session.get("tipo_conta") != "empresa":
        flash("Somente empresas podem cadastrar vagas.", "warning")
        return redirect(url_for("login"))

    conn = None
    cursor = None

    try:
        empresa_id = session["usuario_id"]

        if request.method == "POST":
            titulo = request.form.get("titulo", "").strip()
            descricao = request.form.get("descricao", "").strip()
            requisitos = request.form.get("requisitos", "").strip()
            salario = request.form.get("salario", "").strip()
            localizacao = request.form.get("localizacao", "").strip()
            tipo_contrato = request.form.get("tipo_contrato", "").strip()
            modalidade = request.form.get("modalidade", "").strip()

            if not titulo:
                flash("Informe o título da vaga.", "danger")
                return render_template("nova-vaga.html")

            if not descricao:
                flash("Informe a descrição da vaga.", "danger")
                return render_template("nova-vaga.html")

            if not requisitos:
                flash("Informe os requisitos da vaga.", "danger")
                return render_template("nova-vaga.html")

            if not localizacao:
                flash("Informe a localização da vaga.", "danger")
                return render_template("nova-vaga.html")

            if tipo_contrato not in ["CLT", "PJ", "Estágio", "Freelancer"]:
                flash("Selecione um tipo de contrato válido.", "danger")
                return render_template("nova-vaga.html")

            if modalidade not in ["Presencial", "Híbrido", "Remoto"]:
                flash("Selecione uma modalidade válida.", "danger")
                return render_template("nova-vaga.html")

            conn = get_connection()
            cursor = conn.cursor()

            cursor.execute(
                """
                INSERT INTO vagas (
                    empresa_id,
                    titulo,
                    descricao,
                    requisitos,
                    salario,
                    localizacao,
                    tipo_contrato,
                    modalidade
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """,
                (
                    empresa_id,
                    titulo,
                    descricao,
                    requisitos,
                    salario,
                    localizacao,
                    tipo_contrato,
                    modalidade
                )
            )
            conn.commit()

            flash("Vaga cadastrada com sucesso!", "success")
            return redirect(url_for("nova_vaga"))

        return render_template("nova-vaga.html")

    except Error as e:
        flash(f"Erro no banco de dados: {str(e)}", "danger")
        return render_template("nova-vaga.html")

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

# LISTAR VAGAS
# Usuário: pode se candidatar
# Empresa: pode editar suas próprias vagas
@app.route("/vagas")
def listar_vagas():
    if "usuario_id" not in session:
        flash("Faça login para visualizar as vagas.", "warning")
        return redirect(url_for("login"))

    conn = None
    cursor = None

    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        if session.get("tipo_conta") == "usuario":
            cursor.execute("""
                SELECT 
                    v.id,
                    v.titulo,
                    v.descricao,
                    v.requisitos,
                    v.salario,
                    v.localizacao,
                    v.tipo_contrato,
                    v.modalidade,
                    v.criado_em,
                    e.nome_empresa,
                    CASE 
                        WHEN c.id IS NOT NULL THEN 1
                        ELSE 0
                    END AS ja_candidatado
                FROM vagas v
                INNER JOIN empresas e ON v.empresa_id = e.id
                LEFT JOIN candidaturas c 
                    ON c.vaga_id = v.id AND c.usuario_id = %s
                ORDER BY v.criado_em DESC
            """, (session["usuario_id"],))
        else:
            cursor.execute("""
                SELECT 
                    v.id,
                    v.titulo,
                    v.descricao,
                    v.requisitos,
                    v.salario,
                    v.localizacao,
                    v.tipo_contrato,
                    v.modalidade,
                    v.criado_em,
                    e.nome_empresa,
                    CASE 
                        WHEN v.empresa_id = %s THEN 1
                        ELSE 0
                    END AS minha_vaga
                FROM vagas v
                INNER JOIN empresas e ON v.empresa_id = e.id
                ORDER BY v.criado_em DESC
            """, (session["usuario_id"],))

        vagas = cursor.fetchall()
        return render_template("vagas.html", vagas=vagas, tipo=session.get("tipo_conta"))

    except Error as e:
        flash(f"Erro no banco de dados: {str(e)}", "danger")
        return redirect(url_for("feed"))

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

# CANDIDATAR-SE À VAGA (somente usuário)
# Evita candidatura duplicada
@app.route("/candidatar/<int:vaga_id>", methods=["POST"])
def candidatar_vaga(vaga_id):
    if "usuario_id" not in session or session.get("tipo_conta") != "usuario":
        flash("Somente usuários podem se candidatar às vagas.", "warning")
        return redirect(url_for("login"))

    conn = None
    cursor = None

    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("SELECT id FROM vagas WHERE id = %s", (vaga_id,))
        vaga = cursor.fetchone()

        if not vaga:
            flash("Vaga não encontrada.", "danger")
            return redirect(url_for("listar_vagas"))

        cursor.execute("""
            SELECT id FROM candidaturas
            WHERE usuario_id = %s AND vaga_id = %s
        """, (session["usuario_id"], vaga_id))
        candidatura_existente = cursor.fetchone()

        if candidatura_existente:
            flash("Você já se candidatou para essa vaga.", "warning")
            return redirect(url_for("listar_vagas"))

        cursor.execute("""
            INSERT INTO candidaturas (usuario_id, vaga_id)
            VALUES (%s, %s)
        """, (session["usuario_id"], vaga_id))
        conn.commit()

        flash("Candidatura realizada com sucesso!", "success")
        return redirect(url_for("listar_vagas"))

    except Error as e:
        flash(f"Erro no banco de dados: {str(e)}", "danger")
        return redirect(url_for("listar_vagas"))

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

# EDITAR VAGA (somente empresa)
# Só pode editar vagas que ela mesma criou
@app.route("/editar-vaga/<int:vaga_id>", methods=["GET", "POST"])
def editar_vaga(vaga_id):
    if "usuario_id" not in session or session.get("tipo_conta") != "empresa":
        flash("Somente empresas podem editar vagas.", "warning")
        return redirect(url_for("login"))

    conn = None
    cursor = None

    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("""
            SELECT * FROM vagas
            WHERE id = %s AND empresa_id = %s
        """, (vaga_id, session["usuario_id"]))
        vaga = cursor.fetchone()

        if not vaga:
            flash("Você não tem permissão para editar essa vaga.", "danger")
            return redirect(url_for("listar_vagas"))

        if request.method == "POST":
            titulo = request.form.get("titulo", "").strip()
            descricao = request.form.get("descricao", "").strip()
            requisitos = request.form.get("requisitos", "").strip()
            salario = request.form.get("salario", "").strip()
            localizacao = request.form.get("localizacao", "").strip()
            tipo_contrato = request.form.get("tipo_contrato", "").strip()
            modalidade = request.form.get("modalidade", "").strip()

            if not titulo:
                flash("Informe o título da vaga.", "danger")
                return render_template("editar-vaga.html", vaga=vaga)

            if not descricao:
                flash("Informe a descrição da vaga.", "danger")
                return render_template("editar-vaga.html", vaga=vaga)

            if not requisitos:
                flash("Informe os requisitos da vaga.", "danger")
                return render_template("editar-vaga.html", vaga=vaga)

            if not localizacao:
                flash("Informe a localização da vaga.", "danger")
                return render_template("editar-vaga.html", vaga=vaga)

            if tipo_contrato not in ["CLT", "PJ", "Estágio", "Freelancer"]:
                flash("Selecione um tipo de contrato válido.", "danger")
                return render_template("editar-vaga.html", vaga=vaga)

            if modalidade not in ["Presencial", "Híbrido", "Remoto"]:
                flash("Selecione uma modalidade válida.", "danger")
                return render_template("editar-vaga.html", vaga=vaga)

            cursor.execute("""
                UPDATE vagas
                SET
                    titulo = %s,
                    descricao = %s,
                    requisitos = %s,
                    salario = %s,
                    localizacao = %s,
                    tipo_contrato = %s,
                    modalidade = %s
                WHERE id = %s AND empresa_id = %s
            """, (
                titulo,
                descricao,
                requisitos,
                salario,
                localizacao,
                tipo_contrato,
                modalidade,
                vaga_id,
                session["usuario_id"]
            ))
            conn.commit()

            flash("Vaga atualizada com sucesso!", "success")
            return redirect(url_for("listar_vagas"))

        return render_template("editar-vaga.html", vaga=vaga)

    except Error as e:
        flash(f"Erro no banco de dados: {str(e)}", "danger")
        return redirect(url_for("listar_vagas"))

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

# DOWNLOAD DE CURRÍCULO (PDF)
# Protegido: só logado pode acessar
@app.route("/uploads/<filename>")
def download_arquivo(filename):
    if "usuario_id" not in session:
        flash("Faça login para acessar o arquivo.", "warning")
        return redirect(url_for("login"))
    return send_from_directory(app.config["UPLOAD_FOLDER"], filename)


# DOWNLOAD DE CURRÍCULO (PDF)
# Protegido: só logado pode acessar
@app.route("/logout")
def logout():
    session.clear()
    flash("Você saiu da conta com sucesso.", "success")
    return redirect(url_for("login"))

if __name__ == "__main__":
    app.run(debug=True)