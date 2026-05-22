from sqlalchemy import text

async def render(request, context):

    user_id = context["request"].state.participante_id
    db = context["db"]

    usuario_html = ""

    if user_id:
        row = (
            await db.execute(
                text("""
                SELECT nome, ra
                FROM plataforma.participante
                WHERE id = :id
                """),
                {"id": user_id}
            )
        ).mappings().first()

        if row:
            nome = row["nome"]
            ra = row["ra"]

            usuario_html = f"""
            <div class="user-box" onclick="location.href='/logout'">
                <div class="user-nome">{nome}</div>
                <div class="user-ra">{ra}</div>
            </div>
            """

    else:
        usuario_html = """
        <div class="user-box login" onclick="location.href='/login'">
            Fazer login
        </div>
        """

    body = f"""
    <div class="logo">
        <img src="/logo.png" alt="Logo">
    </div>

    {usuario_html}

    <a href="/">Início</a>
    <a href="/encontro"> &nbsp; &nbsp;Encontros</a>
    <a href="/tarefa"> &nbsp; &nbsp;Tarefas</a>
    <a href="/ranking">Ranking semestral</a>
    <a href="/equipe">Equipe</a>

    <hr/><br>

    <h3>Ferramentas de Desenvolvimento</h3><br>
    <a href="/mapa.pdf" target="_blank">Mapa do Site</a>
    <a href="/fluxo.pdf" target="_blank">Fluxo de Acesso</a>
    <a href="/erro">Últimos Erros</a>
    """

    style = """
    .user-box {
        margin: 15px 10px;
        padding: 12px;
        background: #2a2f36;
        border-radius: 10px;
        cursor: pointer;
        transition: 0.2s;
        border: 1px solid #444;
    }

    .user-box:hover {
        background: #3a4048;
        transform: scale(1.02);
    }

    .user-nome {
        font-weight: bold;
        color: #fff;
        font-size: 14px;
    }

    .user-ra {
        font-size: 12px;
        color: #aaa;
    }

    .user-box.login {
        text-align: center;
        font-weight: bold;
        color: #6ee7b7;
    }

    .user-box.login:hover {
        background: #1f3d2b;
    }
    """

    return {
        "body": body,
        "style": style
    }
