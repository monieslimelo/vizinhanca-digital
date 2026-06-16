from flask import Flask, render_template, request, session, redirect, url_for
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3

app = Flask(__name__)
app.secret_key = "vizinhanca_digital_123"


def conectar_banco():
    return sqlite3.connect("banco.db")


def limpar_documento(valor):
    return ''.join(filter(str.isdigit, valor))


def inicializar_banco():
    conexao = conectar_banco()
    cursor = conexao.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            senha TEXT NOT NULL,
            cpf TEXT UNIQUE,
            cnpj TEXT UNIQUE,
            pontos INTEGER DEFAULT 0,
            tipo TEXT NOT NULL DEFAULT 'cliente'
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS produtos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            descricao TEXT NOT NULL,
            pontos INTEGER NOT NULL,
            imagem TEXT
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

    produtos = [
        ("Arroz Tipo 1", "Pacote 1kg", 500, "arroz.png"),
        ("Feijão Preto", "Pacote 1kg", 400, "feijao.png"),
        ("Óleo de Soja", "900ml", 300, "oleo.png"),
        ("Açúcar Cristal", "Pacote 1kg", 250, "arroz.png"),
        ("Café Tradicional", "Pacote 250g", 350, "feijao.png"),
        ("Macarrão Espaguete", "Pacote 500g", 200, "oleo.png"),
        ("Leite Integral", "Caixa 1L", 300, "arroz.png"),
        ("Biscoito Cream Cracker", "Pacote 350g", 180, "feijao.png"),
    ]

    for produto in produtos:
        cursor.execute("""
            INSERT INTO produtos (nome, descricao, pontos, imagem)
            SELECT ?, ?, ?, ?
            WHERE NOT EXISTS (
                SELECT 1 FROM produtos WHERE nome = ?
            )
        """, (produto[0], produto[1], produto[2], produto[3], produto[0]))

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
            SELECT id, nome, email, senha, tipo
            FROM usuarios
            WHERE email = ?
        """, (email,))

        usuario = cursor.fetchone()
        conexao.close()

        if usuario and check_password_hash(usuario[3], senha_digitada):
            session["usuario_id"] = usuario[0]
            session["nome"] = usuario[1]
            session["email"] = usuario[2]
            session["tipo"] = usuario[4]

            if usuario[4] == "comerciante":
                return redirect("/comerciante")

            return redirect("/dashboard")

        return render_template(
            "login.html",
            mensagem="E-mail ou senha inválidos."
        )

    return render_template("login.html")


@app.route("/cadastro", methods=["GET", "POST"])
def cadastro():
    if request.method == "POST":
        nome = request.form["nome"]
        email = request.form["email"]
        senha = generate_password_hash(request.form["senha"])
        tipo = request.form["tipo"]
        cpf = limpar_documento(request.form["cpf"])

        if len(cpf) != 11:
            return render_template(
                "erro.html",
                titulo="CPF inválido",
                mensagem="Digite um CPF com exatamente 11 números."
            )

        conexao = conectar_banco()
        cursor = conexao.cursor()

        try:
            cursor.execute("""
                INSERT INTO usuarios
                (nome, email, senha, cpf, pontos, tipo)
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
                mensagem="E-mail ou CPF já cadastrado."
            )

    return render_template("cadastro.html")


@app.route("/dashboard")
def dashboard():
    if "email" not in session:
        return redirect("/login")

    if session.get("tipo") == "comerciante":
        return redirect("/comerciante")

    conexao = conectar_banco()
    cursor = conexao.cursor()

    cursor.execute("""
        SELECT nome, pontos, tipo
        FROM usuarios
        WHERE email = ?
    """, (session["email"],))

    usuario = cursor.fetchone()

    cursor.execute("SELECT COUNT(*) FROM produtos")
    total_produtos = cursor.fetchone()[0]

    cursor.execute("""
        SELECT COUNT(*)
        FROM historico
        WHERE email = ?
    """, (session["email"],))

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

    if session.get("tipo") == "comerciante":
        return redirect("/comerciante")

    conexao = conectar_banco()
    cursor = conexao.cursor()

    cursor.execute("""
        SELECT nome, pontos
        FROM usuarios
        WHERE email = ?
    """, (session["email"],))

    usuario = cursor.fetchone()

    cursor.execute("""
        SELECT id, nome, descricao, pontos, imagem
        FROM produtos
    """)

    produtos = cursor.fetchall()
    conexao.close()

    return render_template(
        "catalogo.html",
        produtos=produtos,
        nome=usuario[0],
        pontos_usuario=usuario[1]
    )


@app.route("/resgatar/<int:produto_id>")
def resgatar(produto_id):
    if "email" not in session:
        return redirect("/login")

    if session.get("tipo") == "comerciante":
        return redirect("/comerciante")

    conexao = conectar_banco()
    cursor = conexao.cursor()

    cursor.execute("""
        SELECT nome, pontos
        FROM produtos
        WHERE id = ?
    """, (produto_id,))

    produto = cursor.fetchone()

    if produto is None:
        conexao.close()
        return render_template(
            "erro.html",
            titulo="Produto não encontrado",
            mensagem="Este produto não está disponível."
        )

    nome_produto = produto[0]
    custo = produto[1]

    cursor.execute("""
        SELECT pontos
        FROM usuarios
        WHERE email = ?
    """, (session["email"],))

    usuario = cursor.fetchone()
    pontos_atuais = usuario[0]

    if pontos_atuais < custo:
        conexao.close()
        return render_template(
            "erro.html",
            titulo="Pontos insuficientes",
            mensagem=f"Você tem {pontos_atuais} pontos, mas este produto custa {custo} pontos."
        )

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


@app.route("/historico")
def historico():
    if "email" not in session:
        return redirect("/login")

    if session.get("tipo") == "comerciante":
        return redirect("/comerciante")

    conexao = conectar_banco()
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
    if "usuario_id" not in session:
        return redirect(url_for("login"))

    conexao = conectar_banco()
    conexao.row_factory = sqlite3.Row
    cursor = conexao.cursor()

    cursor.execute("""
        SELECT nome, email, pontos, tipo, cpf
        FROM usuarios
        WHERE id = ?
    """, (session["usuario_id"],))

    usuario = cursor.fetchone()
    conexao.close()

    if usuario is None:
        return redirect(url_for("login"))

    return render_template(
        "perfil.html",
        nome=usuario["nome"],
        email=usuario["email"],
        pontos=usuario["pontos"],
        tipo=usuario["tipo"],
        cpf=usuario["cpf"]
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
        {
            "nome": "Mercadinho Central",
            "tipo": "Mercado de bairro",
            "beneficio": "5% de cashback em compras acima de R$ 50,00",
            "endereco": "Centro - Aracaju/SE",
            "icone": "🛒"
        },
        {
            "nome": "Café da Praça",
            "tipo": "Cafeteria local",
            "beneficio": "2x pontos em produtos selecionados",
            "endereco": "Siqueira Campos - Aracaju/SE",
            "icone": "☕"
        },
        {
            "nome": "Farmácia Popular",
            "tipo": "Farmácia parceira",
            "beneficio": "10% de desconto para clientes cadastrados",
            "endereco": "Santos Dumont - Aracaju/SE",
            "icone": "💊"
        },
        {
            "nome": "Padaria Ideal",
            "tipo": "Panificação parceira",
            "beneficio": "Pão grátis acima de 1000 pontos",
            "endereco": "Farolândia - Aracaju/SE",
            "icone": "🥖"
        },
    ]

    return render_template("parceiros.html", parceiros=parceiros)


@app.route("/comerciante", methods=["GET", "POST"])
def comerciante():
    if "email" not in session:
        return redirect("/login")

    if session.get("tipo") != "comerciante":
        return render_template(
            "erro.html",
            titulo="Acesso negado",
            mensagem="Área exclusiva para comerciantes."
        )

    mensagem = ""

    if request.method == "POST":
        cpf_cliente = limpar_documento(request.form["cpf_cliente"])
        pontos = int(request.form["pontos"])

        conexao = conectar_banco()
        cursor = conexao.cursor()

        cursor.execute("""
            SELECT nome, pontos
            FROM usuarios
            WHERE cpf = ? AND tipo = 'cliente'
        """, (cpf_cliente,))

        cliente = cursor.fetchone()

        if cliente:
            cursor.execute("""
                UPDATE usuarios
                SET pontos = pontos + ?
                WHERE cpf = ?
            """, (pontos, cpf_cliente))

            conexao.commit()
            mensagem = f"✅ {pontos} pontos adicionados para {cliente[0]}."
        else:
            mensagem = "❌ Cliente não encontrado. Verifique se o CPF está correto."

        conexao.close()

    conexao = conectar_banco()
    cursor = conexao.cursor()

    cursor.execute("SELECT COUNT(*) FROM usuarios WHERE tipo = 'cliente'")
    total_clientes = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM produtos")
    total_produtos = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM historico")
    total_resgates = cursor.fetchone()[0]

    cursor.execute("""
        SELECT nome, email, cpf, pontos
        FROM usuarios
        WHERE tipo = 'cliente'
        ORDER BY nome ASC
    """)
    clientes = cursor.fetchall()

    conexao.close()

    return render_template(
        "comerciante.html",
        mensagem=mensagem,
        nome=session.get("nome"),
        email=session.get("email"),
        tipo=session.get("tipo"),
        total_clientes=total_clientes,
        total_produtos=total_produtos,
        total_resgates=total_resgates,
        clientes=clientes
    )


@app.route("/produtos_comerciante")
def produtos_comerciante():
    if "email" not in session:
        return redirect("/login")

    if session.get("tipo") != "comerciante":
        return redirect("/dashboard")

    conexao = conectar_banco()
    cursor = conexao.cursor()

    cursor.execute("""
        SELECT id, nome, descricao, pontos
        FROM produtos
        ORDER BY nome ASC
    """)

    produtos = cursor.fetchall()
    conexao.close()

    return render_template(
        "produtos_comerciante.html",
        produtos=produtos
    )


@app.route("/adicionar_carrinho/<int:produto_id>")
def adicionar_carrinho(produto_id):
    if "email" not in session:
        return redirect("/login")

    if session.get("tipo") == "comerciante":
        return redirect("/comerciante")

    carrinho = session.get("carrinho", [])
    carrinho.append(produto_id)
    session["carrinho"] = carrinho

    return redirect("/carrinho")


@app.route("/carrinho")
def carrinho():
    if "email" not in session:
        return redirect("/login")

    if session.get("tipo") == "comerciante":
        return redirect("/comerciante")

    ids = session.get("carrinho", [])
    produtos_carrinho = []
    total_pontos = 0

    conexao = conectar_banco()
    cursor = conexao.cursor()

    for produto_id in ids:
        cursor.execute("""
            SELECT id, nome, descricao, pontos, imagem
            FROM produtos
            WHERE id = ?
        """, (produto_id,))

        produto = cursor.fetchone()

        if produto:
            produtos_carrinho.append(produto)
            total_pontos += produto[3]

    conexao.close()

    return render_template(
        "carrinho.html",
        produtos=produtos_carrinho,
        total_pontos=total_pontos
    )


@app.route("/limpar_carrinho")
def limpar_carrinho():
    if "email" not in session:
        return redirect("/login")

    if session.get("tipo") == "comerciante":
        return redirect("/comerciante")

    session["carrinho"] = []
    return redirect("/carrinho")


@app.route("/pagamento_pix")
def pagamento_pix():
    if "email" not in session:
        return redirect("/login")

    if session.get("tipo") == "comerciante":
        return redirect("/comerciante")

    ids = session.get("carrinho", [])
    total_pontos = 0

    conexao = conectar_banco()
    cursor = conexao.cursor()

    for produto_id in ids:
        cursor.execute("""
            SELECT pontos
            FROM produtos
            WHERE id = ?
        """, (produto_id,))

        produto = cursor.fetchone()

        if produto:
            total_pontos += produto[0]

    conexao.close()

    return render_template(
        "pagamento_pix.html",
        total_pontos=total_pontos
    )


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")


if __name__ == "__main__":
    app.run(debug=True)