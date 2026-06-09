from flask import Flask, render_template, request, session, redirect
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3

app = Flask(__name__)
app.secret_key = "vizinhanca_digital_123"

def conectar_banco():
    return sqlite3.connect("banco.db")


def usuario_logado():
    return "email" in session


def apenas_comerciante():
    return session.get("tipo") == "comerciante"


def limpar_cpf(cpf):
    return ''.join(filter(str.isdigit, cpf))


def inicializar_banco():
    conexao = conectar_banco()
    cursor = conexao.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS usuarios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL,
        email TEXT NOT NULL UNIQUE,
        senha TEXT NOT NULL,
        cpf TEXT,
        pontos INTEGER DEFAULT 0,
        tipo TEXT NOT NULL DEFAULT 'cliente'
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS historico (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT NOT NULL,
        produto TEXT NOT NULL,
        pontos_usados INTEGER NOT NULL,
        data TEXT DEFAULT CURRENT_TIMESTAMP
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS produtos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL,
        descricao TEXT,
        pontos INTEGER NOT NULL,
        imagem TEXT
    )
    """)

    cursor.execute("""
    INSERT INTO produtos (nome, descricao, pontos, imagem)
    SELECT 'Arroz Tipo 1', 'Pacote 1kg', 500, 'arroz.png'
    WHERE NOT EXISTS (SELECT 1 FROM produtos WHERE nome = 'Arroz Tipo 1')
    """)

    cursor.execute("""
    INSERT INTO produtos (nome, descricao, pontos, imagem)
    SELECT 'Feijão Preto', 'Pacote 1kg', 400, 'feijao.png'
    WHERE NOT EXISTS (SELECT 1 FROM produtos WHERE nome = 'Feijão Preto')
    """)

    cursor.execute("""
    INSERT INTO produtos (nome, descricao, pontos, imagem)
    SELECT 'Óleo de Soja', '900ml', 300, 'oleo.png'
    WHERE NOT EXISTS (SELECT 1 FROM produtos WHERE nome = 'Óleo de Soja')
    """)

    conexao.commit()
    conexao.close()


inicializar_banco()


@app.route("/")
def home():
    return redirect("/login")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        senha_digitada = request.form["senha"]

        conexao = conectar_banco()
        cursor = conexao.cursor()

        cursor.execute("""
            SELECT nome, email, senha, tipo FROM usuarios
            WHERE email = ?
        """, (email,))

        usuario = cursor.fetchone()
        conexao.close()

        if usuario and check_password_hash(usuario[2], senha_digitada):
            session["nome"] = usuario[0]
            session["email"] = usuario[1]
            session["tipo"] = usuario[3]

            if usuario[3] == "comerciante":
                return redirect("/comerciante")
            else:
                return redirect("/dashboard")

        return "<h1>Email ou senha inválidos!</h1><a href='/login'>Voltar</a>"

    return render_template("login.html")


@app.route("/cadastro", methods=["GET", "POST"])
def cadastro():
    if request.method == "POST":
        nome = request.form["nome"]
        cpf = limpar_cpf(request.form["cpf"])

        if len(cpf) != 11:
            return render_template(
                "erro.html",
                titulo="CPF inválido",
                mensagem="Digite um CPF com exatamente 11 números."
            )

        email = request.form["email"]
        senha = generate_password_hash(request.form["senha"])
        tipo = request.form["tipo"]

        conexao = conectar_banco()
        cursor = conexao.cursor()

        try:
            cursor.execute("""
                INSERT INTO usuarios (nome, email, senha, cpf, pontos, tipo)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (nome, email, senha, cpf, 1000, tipo))

            conexao.commit()
            conexao.close()

            return redirect("/login")

        except sqlite3.IntegrityError:
            conexao.close()
            return render_template(
                "erro.html",
                titulo="Cadastro inválido",
                mensagem="Este e-mail ou CPF já está cadastrado."
            )

    return render_template("cadastro.html")

@app.route("/dashboard")
def dashboard():
    if "email" not in session:
        return redirect("/login")

    conexao = sqlite3.connect("banco.db")
    cursor = conexao.cursor()

    cursor.execute("SELECT nome, pontos, tipo FROM usuarios WHERE email = ?", (session["email"],))
    usuario = cursor.fetchone()

    cursor.execute("SELECT COUNT(*) FROM produtos")
    total_produtos = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM historico WHERE email = ?", (session["email"],))
    total_resgates = cursor.fetchone()[0]

    conexao.close()

    return render_template(
        "dashboard.html",
        nome=usuario[0],
        pontos=usuario[1],
        tipo=usuario[2],
        total_produtos=total_produtos,
        total_parceiros=4,
        total_resgates=total_resgates
    )


@app.route("/catalogo")
def catalogo():
    if "email" not in session:
        return redirect("/login")

    conexao = sqlite3.connect("banco.db")
    cursor = conexao.cursor()

    cursor.execute("""
        SELECT id, nome, descricao, pontos, imagem
        FROM produtos
    """)

    produtos = cursor.fetchall()
    conexao.close()

    return render_template("catalogo.html", produtos=produtos)


@app.route("/resgatar/<int:produto_id>")
def resgatar(produto_id):
    if "email" not in session:
        return redirect("/login")

    conexao = sqlite3.connect("banco.db")
    cursor = conexao.cursor()

    cursor.execute("""
        SELECT nome, pontos FROM produtos
        WHERE id = ?
    """, (produto_id,))

    produto = cursor.fetchone()

    if produto is None:
        conexao.close()
        return "Produto não encontrado."

    nome_produto = produto[0]
    custo = produto[1]

    cursor.execute("""
        SELECT pontos FROM usuarios
        WHERE email = ?
    """, (session["email"],))

    usuario = cursor.fetchone()
    pontos_atuais = usuario[0]

    if pontos_atuais < custo:
        conexao.close()
        return f"""
        <h1>Pontos insuficientes!</h1>
        <p>Você tem {pontos_atuais} pontos.</p>
        <p>Este produto custa {custo} pontos.</p>
        <a href="/catalogo">Voltar ao catálogo</a>
        """

    novos_pontos = pontos_atuais - custo

    cursor.execute("""
        UPDATE usuarios
        SET pontos = ?
        WHERE email = ?
    """, (novos_pontos, session["email"]))

    cursor.execute("""
        INSERT INTO historico (email, produto, pontos_usados)
        VALUES (?, ?, ?)
    """, (session["email"], nome_produto, custo))

    conexao.commit()
    conexao.close()

    return render_template(
        "resgate_sucesso.html",
        produto=nome_produto,
        pontos=novos_pontos
    )


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")


@app.route("/historico")
def historico():
    if "email" not in session:
        return redirect("/login")

    conexao = sqlite3.connect("banco.db")
    cursor = conexao.cursor()

    cursor.execute("""
        SELECT produto, pontos_usados, data
        FROM historico
        WHERE email = ?
        ORDER BY id DESC
    """, (session["email"],))

    historico = cursor.fetchall()
    conexao.close()

    return render_template("historico.html", historico=historico)


@app.route("/perfil")
def perfil():
    if "email" not in session:
        return redirect("/login")

    conexao = sqlite3.connect("banco.db")
    cursor = conexao.cursor()

    cursor.execute("""
        SELECT nome, email, pontos FROM usuarios
        WHERE email = ?
    """, (session["email"],))

    usuario = cursor.fetchone()
    conexao.close()

    return render_template(
        "perfil.html",
        nome=usuario[0],
        email=usuario[1],
        pontos=usuario[2]
    )


@app.route("/beneficios")
def beneficios():
    if "email" not in session:
        return redirect("/login")

    return render_template("beneficios.html")


@app.route("/parceiros")
def parceiros():
    if "email" not in session:
        return redirect("/login")

    parceiros = [
        {"nome": "Mercadinho Central", "beneficio": "5% de cashback",               "icone": "🛒"},
        {"nome": "Café da Praça",       "beneficio": "2x pontos no café",            "icone": "☕"},
        {"nome": "Farmácia Popular",    "beneficio": "10% desconto",                 "icone": "💊"},
        {"nome": "Padaria Ideal",       "beneficio": "Pão grátis acima de 1000 pontos", "icone": "🥖"},
    ]

    return render_template("parceiros.html", parceiros=parceiros)


@app.route("/comerciante", methods=["GET", "POST"])
def comerciante():
    if "email" not in session:
        return redirect("/login")

    # Usa o tipo já salvo na sessão — sem abrir o banco
    if session.get("tipo") != "comerciante":
        return """
        <h1>Acesso negado!</h1>
        <p>Área exclusiva para comerciantes.</p>
        <a href='/dashboard'>Voltar</a>
        """

    mensagem = ""

    if request.method == "POST":
        email_cliente = request.form["email_cliente"]
        pontos = int(request.form["pontos"])

        conexao = sqlite3.connect("banco.db")
        cursor = conexao.cursor()

        cursor.execute("""
            SELECT * FROM usuarios
            WHERE email = ?
        """, (email_cliente,))

        usuario = cursor.fetchone()

        if usuario:
            cursor.execute("""
                UPDATE usuarios
                SET pontos = pontos + ?
                WHERE email = ?
            """, (pontos, email_cliente))

            conexao.commit()
            mensagem = f"✅ {pontos} pontos adicionados para {email_cliente}"
        else:
            mensagem = "❌ Cliente não encontrado"

        conexao.close()

    return render_template("comerciante.html", mensagem=mensagem)


if __name__ == "__main__":
    app.run(debug=True)