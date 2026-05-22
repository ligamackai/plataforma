from sqlalchemy import text

async def render(request, context):
    db = context["db"]

    # ============================
    # SEMESTRE ATUAL
    # ============================

    result = await db.execute(text("""
        SELECT id, descricao
        FROM plataforma.semestre
        ORDER BY id DESC
        LIMIT 1
    """))

    semestre = result.mappings().first()
    semestre_id = semestre["id"]
    semestre_desc = semestre["descricao"]

    # ============================
    # GRUPOS + OCORRÊNCIA
    # ============================

    result = await db.execute(text("""
        SELECT
            g.id,
            g.nome,
            g.tipo,
            g.descricao,
            CASE 
                WHEN o.id IS NULL THEN FALSE
                ELSE TRUE
            END AS ativo
        FROM plataforma.grupo g
        LEFT JOIN plataforma.ocorreu o
            ON o.grupo = g.id
            AND o.semestre = :semestre
        ORDER BY g.nome
    """), {"semestre": semestre_id})

    rows = result.mappings().all()

    ativos = []
    inativos = []

    for r in rows:
        if r["ativo"]:
            ativos.append(r)
        else:
            inativos.append(r)

    # ============================
    # HTML
    # ============================

    html = f"""
        <div class="header-grupos">
            <h1>Grupos</h1>
            <div class="semestre">Semestre atual: {semestre_desc}</div>
        </div>
	    <a href="/grupo/novo" class="side-btn">
		+ Novo grupo
	    </a>
	    <a href="/grupo/ativar" class="side-btn">
		+ Ativar grupo
	    </a>

        <h2>🟢 Ativos neste semestre</h2>

        <div class="cards">
            {''.join([f'''
                <a class="card" href="/grupo/{r['id']}">

                    <div class="thumb"></div>

                    <div class="content">

                        <div class="grupo">
                            {r['nome']}
                        </div>

                        <div class="tipo">
                            {r['tipo']}
                        </div>

                        <div class="descricao">
                            {r['descricao']}
                        </div>

                    </div>

                </a>
            ''' for r in ativos]) or "<div class='empty'>Nenhum grupo ativo neste semestre</div>"}
        </div>

        <h2>⚪ Inativos neste semestre</h2>

        <div class="cards">
            {''.join([f'''
                <a class="card alt" href="/grupo/{r['id']}">

                    <div class="thumb"></div>

                    <div class="content">

                        <div class="grupo">
                            {r['nome']}
                        </div>

                        <div class="tipo">
                            {r['tipo']}
                        </div>

                        <div class="descricao">
                            {r['descricao']}
                        </div>

                    </div>

                </a>
            ''' for r in inativos]) or "<div class='empty'>Nenhum grupo inativo</div>"}
        </div>
    """

    # ============================
    # STYLE
    # ============================

    style = """

    .cards {
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
        gap: 16px;
    }

    .card {
        display: block;
        text-decoration: none;
        color: white;
        border-radius: 14px;
        overflow: hidden;
        background: #1a1a1f;
        transition: 0.2s;
        box-shadow: 0 4px 20px rgba(0,0,0,0.4);
    }

    .card.alt {
        background: #222228;
        opacity: 0.7;
    }

    .card:hover {
        background: #2a2a30;
        transform: translateY(-3px);
    }

    .card:active {
        background: #333;
    }

    .thumb {
        height: 90px;
        background: linear-gradient(135deg, #006400, #00cc66);
        opacity: 0.35;
    }

    .card.alt .thumb {
        background: linear-gradient(135deg, #444, #888);
    }

    .content {
        padding: 12px;
    }

    .grupo {
        font-size: 18px;
        font-weight: bold;
        color: #00cc66;
        margin-bottom: 4px;
    }

    .card.alt .grupo {
        color: #aaa;
    }

    .tipo {
        font-size: 13px;
        color: #bbb;
        margin-bottom: 6px;
    }

    .descricao {
        font-size: 13px;
        color: #999;
        line-height: 1.4;
    }

    .empty {
        color: #888;
        padding: 10px;
    }

    .header-grupos{
        display:flex;
        align-items:center;
        justify-content:space-between;
        margin-bottom:20px;
    }

    .header-grupos h1{
        margin:0;
    }

    .semestre{
        color:#aaa;
        font-size:14px;
    }
    """

    return {
        "title": "Grupos",
        "body": html,
        "style": style
    }
