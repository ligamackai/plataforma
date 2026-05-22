from sqlalchemy import text

async def render(request, context):
    db = context["db"]

    # ============================
    # GET PARAMETERS
    # ============================

    get = request.get("query", {})
    semestre_get = get.get("semestre")

    # ============================
    # LISTA DE SEMESTRES
    # ============================

    result = await db.execute(text("""
        SELECT id, descricao
        FROM plataforma.semestre
        ORDER BY id DESC
    """))

    semestres = result.mappings().all()

    if not semestres:
        return {
            "title": "Ranking",
            "body": "<div class='empty'>Nenhum semestre cadastrado</div>"
        }

    # ============================
    # DEFINIR SEMESTRE ATUAL
    # ============================

    semestre_atual = semestres[0]

    semestre_id = semestre_atual["id"]
    semestre_desc = semestre_atual["descricao"]

    if semestre_get:
        for s in semestres:
            if s["descricao"] == semestre_get:
                semestre_id = s["id"]
                semestre_desc = s["descricao"]
                break

    # ============================
    # RANKING
    # ============================

    result = await db.execute(text("""
        SELECT
            p.id,
            p.nome,
            SUM(h.horas) AS horas
        FROM plataforma.horas h
        JOIN plataforma.participante p ON p.id = h.participante
        WHERE h.semestre = :semestre
        GROUP BY p.id, p.nome
        ORDER BY horas DESC
    """), {"semestre": semestre_id})

    ranking = result.mappings().all()

    # ============================
    # ABAS DE SEMESTRE
    # ============================

    tabs = ""

    for s in semestres:
        active = "active" if s["id"] == semestre_id else ""

        tabs += f"""
            <a class="tab {active}" href="/ranking?semestre={s['descricao']}">
                {s['descricao']}
            </a>
        """

    # ============================
    # RENDER RANKING
    # ============================

    rows = ""

    for i, r in enumerate(ranking):

        medal = ""
        classe = ""

        if i == 0:
            classe = "gold"
            medal = "🥇"
        elif i == 1:
            classe = "silver"
            medal = "🥈"
        elif i == 2:
            classe = "bronze"
            medal = "🥉"

        rows += f"""
            <div class="row {classe}">
                <div class="pos">{i+1}</div>
                <div class="nome">{r['nome']}</div>
                <div class="horas">{r['horas']}h</div>
                <div class="medal">{medal}</div>
            </div>
        """

    if not rows:
        rows = "<div class='empty'>Nenhuma hora registrada neste semestre</div>"

    # ============================
    # HTML
    # ============================

    html = f"""
        <h1>Ranking</h1>

        <div class="tabs">
            {tabs}
        </div>

        <div class="ranking">
            {rows}
        </div>
    """

    # ============================
    # STYLE
    # ============================

    style = """

    .tabs{
        display:flex;
        gap:10px;
        overflow-x:auto;
        margin-bottom:20px;
        padding-bottom:4px;
    }

    .tab{
        padding:8px 14px;
        border-radius:10px;
        background:#1a1a1f;
        color:#ccc;
        text-decoration:none;
        white-space:nowrap;
        transition:0.2s;
    }

    .tab:hover{
        background:#2a2a30;
    }

    .tab.active{
        background:#ff4d4d;
        color:white;
    }

    .ranking{
        display:flex;
        flex-direction:column;
        gap:10px;
    }

    .row{
        display:grid;
        grid-template-columns:60px 1fr 80px 50px;
        align-items:center;
        padding:12px;
        border-radius:10px;
        background:#1a1a1f;
    }

    .row.gold{
        border:2px solid gold;
    }

    .row.silver{
        border:2px solid silver;
    }

    .row.bronze{
        border:2px solid #cd7f32;
    }

    .pos{
        font-weight:bold;
        font-size:18px;
        color:#aaa;
    }

    .nome{
        font-size:16px;
    }

    .horas{
        text-align:right;
        color:#ccc;
    }

    .medal{
        text-align:center;
        font-size:18px;
    }

    .empty{
        color:#888;
        padding:10px;
    }
    """

    return {
        "title": f"Ranking {semestre_desc}",
        "body": html,
        "style": style
    }
