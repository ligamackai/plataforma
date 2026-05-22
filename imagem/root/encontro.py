from sqlalchemy import text
from datetime import datetime, timezone

def _fmt_dt(dt):
    if dt is None:
        return ""
    return dt.strftime("%d/%m/%Y %H:%M")

async def render(request, context):
    db = context["db"]
    now = datetime.now(timezone.utc)
    query = request.get("query", {})
    grupo_id = query.get("grupo")

    extra = ""
    if grupo_id:
        extra = f"AND g.id = {grupo_id}"

    result = await db.execute(text(f"""
        SELECT 
            e.id,
            e.tema,
            e.inicio,
            e.fim,
            g.nome AS grupo
        FROM plataforma.encontro e
        JOIN plataforma.ocorreu o ON o.id = e.ocorrencia
        JOIN plataforma.grupo g ON g.id = o.grupo
        WHERE e.valido = TRUE {extra}
        ORDER BY e.inicio DESC
    """))

    rows = result.mappings().all()

    futuros = []
    passados = []

    for r in rows:
        if r["inicio"] >= now:
            futuros.append(r)
        else:
            passados.append(r)

    futuros.sort(key=lambda x: x["inicio"])

    html = f"""
        <div class="header-encontros">
            <h1>Encontros</h1>
            <a href="/encontro/agendar" class="btn-agendar">
                + Agendar encontro
            </a>
        </div>
        <h2>📅 Próximos encontros</h2>
        <div class="cards">
            {''.join([f'''
                <a class="card" href="/encontro/{r['id']}">
                    <div class="thumb"></div>
                    <div class="content">

                        <div class="grupo">{r['grupo']}</div>

                        <div class="tema">{r['tema']}</div>

                        <div class="tempo">
                            <span>Início:</span> {_fmt_dt(r['inicio'])}<br>
                            <span>Fim:</span> {_fmt_dt(r['fim'])}
                        </div>

                    </div>
                </a>
            ''' for r in futuros]) or "<div class='empty'>Nenhum encontro futuro</div>"}
        </div>

        <h2>📚 Já realizados</h2>
        <div class="cards">
            {''.join([f'''
                <a class="card alt" href="/encontro/{r['id']}">
                    <div class="thumb"></div>
                    <div class="content">

                        <div class="grupo">{r['grupo']}</div>

                        <div class="tema">{r['tema']}</div>

                        <div class="tempo">
                            <span>Início:</span> {_fmt_dt(r['inicio'])}
                        </div>

                    </div>
                </a>
            ''' for r in passados]) or "<div class='empty'>Nenhum encontro passado</div>"}
        </div>
    """

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
        background: linear-gradient(135deg, #b30000, #ff4d4d);
        opacity: 0.4;
    }

    .content {
        padding: 12px;
    }

    .grupo {
        font-size: 18px;
        font-weight: bold;
        color: #ff4d4d;
        margin-bottom: 4px;
    }

    /* tema secundário */
    .tema {
        font-size: 14px;
        margin-bottom: 8px;
        color: #ddd;
    }

    .tempo {
        font-size: 13px;
        color: #aaa;
        line-height: 1.4;
    }

    .tempo span {
        color: #888;
    }

    .empty {
        color: #888;
        padding: 10px;
    }

    .topbar {
        display: flex;
        justify-content: flex-end;
        margin-bottom: 20px;
    }

    .btn-agendar {
        background: linear-gradient(135deg, #b30000, #ff4d4d);
        color: white;
        text-decoration: none;
        padding: 10px 16px;
        border-radius: 10px;
        font-weight: 600;
        font-size: 14px;
        transition: 0.2s;
        box-shadow: 0 4px 12px rgba(179, 0, 0, 0.4);
    }

    .btn-agendar:hover {
        transform: translateY(-2px);
        background: linear-gradient(135deg, #cc0000, #ff6666);
    }

    .btn-agendar:active {
        transform: scale(0.96);
        background: #990000;
    }
    .header-encontros{
        display:flex;
        align-items:center;
        justify-content:space-between;
        margin-bottom:20px;
    }

    .header-encontros h1{
        margin:0;
    }
    """

    return {
        "title": "Encontros",
        "body": html,
        "style": style
    }
