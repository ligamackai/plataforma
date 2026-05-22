from sqlalchemy import text
from datetime import datetime, timezone

def _fmt(dt):
    if not dt:
        return ""
    return dt.strftime("%d/%m/%Y")

async def render(request, context):

    db = context["db"]
    now = datetime.now(timezone.utc)

    # ============================
    # CARGOS ATIVOS
    # ============================

    result = await db.execute(text("""
        SELECT
            c.id,
            p.nome AS participante,
            tc.nome AS tipo,
            tc.id AS tipo_id,
            c.inicio,
            c.fim
        FROM plataforma.cargo c
        JOIN plataforma.participante p ON p.id = c.participante
        JOIN plataforma.tipo_cargo tc ON tc.id = c.tipo
        WHERE c.ativo = TRUE
        AND (
            c.fim IS NULL
            OR c.fim > now()
        )
        ORDER BY
            tc.id ASC,
            c.inicio ASC
    """))

    ativos = result.mappings().all()

    # ============================
    # CARGOS PASSADOS
    # ============================

    result = await db.execute(text("""
        SELECT
            c.id,
            p.nome AS participante,
            tc.nome AS tipo,
            c.inicio,
            c.fim
        FROM plataforma.cargo c
        JOIN plataforma.participante p ON p.id = c.participante
        JOIN plataforma.tipo_cargo tc ON tc.id = c.tipo
        WHERE
            c.fim IS NOT NULL
            AND c.fim <= now()
        ORDER BY
            c.fim DESC
    """))

    passados = result.mappings().all()

    # ============================
    # HTML ATIVOS
    # ============================

    html_ativos = ""

    for r in ativos:

        fim = "Atual" if r["fim"] is None else _fmt(r["fim"])

        html_ativos += f"""
        <a class="card" href="/equipe/{r['id']}">
            <div class="cargo">{r['tipo']}</div>
            <div class="nome">{r['participante']}</div>

            <div class="tempo">
                {_fmt(r['inicio'])} → {fim}
            </div>
        </a>
        """

    if not html_ativos:
        html_ativos = "<div class='empty'>Nenhum cargo ativo</div>"

    # ============================
    # HTML PASSADOS
    # ============================

    html_passados = ""

    for r in passados:

        html_passados += f"""
        <a class="card alt" href="/equipe/{r['id']}">
            <div class="cargo">{r['tipo']}</div>
            <div class="nome">{r['participante']}</div>

            <div class="tempo">
                {_fmt(r['inicio'])} → {_fmt(r['fim'])}
            </div>
        </a>
        """

    if not html_passados:
        html_passados = "<div class='empty'>Nenhum cargo passado</div>"

    # ============================
    # HTML FINAL
    # ============================

    html = f"""
    <h1>Cargos</h1>

    <a href="/cargo/novo" class="side-btn">
	+ Novo cargo
    </a>
    <a href="/cargo/atribuir" class="side-btn">
	+ Atribuir cargo
    </a>
    
    <h2>🏛️ Cargos ativos</h2>

    <div class="cards">
        {html_ativos}
    </div>

    <h2>📚 Histórico de cargos</h2>

    <div class="cards">
        {html_passados}
    </div>
    """

    # ============================
    # STYLE
    # ============================

    style = """

    .cards{
        display:grid;
        grid-template-columns:repeat(auto-fill,minmax(260px,1fr));
        gap:16px;
    }

    .card{
        background:#1a1a1f;
        padding:14px;
        border-radius:12px;
        box-shadow:0 4px 20px rgba(0,0,0,0.4);
    }

    .card.alt{
        background:#222228;
        opacity:0.8;
    }

    .cargo{
        font-weight:bold;
        font-size:16px;
        color:#ff4d4d;
        margin-bottom:4px;
    }

    .nome{
        font-size:15px;
        margin-bottom:6px;
    }

    .tempo{
        font-size:13px;
        color:#aaa;
    }

    .empty{
        color:#888;
        padding:10px;
    }

    """

    return {
        "title": "Cargos",
        "body": html,
        "style": style
    }
