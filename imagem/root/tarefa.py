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
            t.id,
            t.tema,
            t.descricao,
            t.inicio,
            t.prazo,
            t.horas,
            t.replicas,
            g.nome AS grupo
        FROM plataforma.tarefa t
        JOIN plataforma.ocorreu o ON o.id = t.ocorrencia
        JOIN plataforma.grupo g ON g.id = o.grupo
        WHERE t.valido = TRUE {extra}
        ORDER BY t.prazo DESC
    """))

    rows = result.mappings().all()

    abertas = []
    encerradas = []

    for r in rows:
        if r["prazo"] >= now:
            abertas.append(r)
        else:
            encerradas.append(r)

    abertas.sort(key=lambda x: x["prazo"])

    html = f"""
        <div class="header-tarefas">
            <h1>Tarefas</h1>
            <a href="/tarefa/criar" class="side-btn">
                + Criar tarefa
            </a>
        </div>

        <h2>📝 Tarefas em aberto</h2>

        <div class="cards">
            {''.join([f'''
                <a class="card" href="/tarefa/{r['id']}">
                    <div class="thumb"></div>

                    <div class="content">

                        <div class="grupo">{r['grupo']}</div>

                        <div class="tema">{r['tema']}</div>

                        <div class="tempo">
                            <span>Início:</span> {_fmt_dt(r['inicio'])}<br>
                            <span>Prazo:</span> {_fmt_dt(r['prazo'])}
                        </div>

                        <div class="meta">
                            {r['horas']}h • {r['replicas']} réplica(s)
                        </div>

                    </div>
                </a>
            ''' for r in abertas]) or "<div class='empty'>Nenhuma tarefa aberta</div>"}
        </div>


        <h2>📚 Tarefas encerradas</h2>

        <div class="cards">
            {''.join([f'''
                <a class="card alt" href="/tarefa/{r['id']}">
                    <div class="thumb"></div>

                    <div class="content">

                        <div class="grupo">{r['grupo']}</div>

                        <div class="tema">{r['tema']}</div>

                        <div class="tempo">
                            <span>Prazo:</span> {_fmt_dt(r['prazo'])}
                        </div>

                        <div class="meta">
                            {r['horas']}h • {r['replicas']} réplica(s)
                        </div>

                    </div>
                </a>
            ''' for r in encerradas]) or "<div class='empty'>Nenhuma tarefa encerrada</div>"}
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
        background: linear-gradient(135deg, #004080, #3399ff);
        opacity: 0.4;
    }

    .content {
        padding: 12px;
    }

    .grupo {
        font-size: 16px;
        font-weight: bold;
        color: #3399ff;
        margin-bottom: 4px;
    }

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

    .meta {
        margin-top: 6px;
        font-size: 12px;
        color: #888;
    }

    .empty {
        color: #888;
        padding: 10px;
    }

    .header-tarefas{
        display:flex;
        align-items:center;
        justify-content:space-between;
        margin-bottom:20px;
    }

    .header-tarefas h1{
        margin:0;
    }
    """

    return {
        "title": "Tarefas",
        "body": html,
        "style": style
    }
