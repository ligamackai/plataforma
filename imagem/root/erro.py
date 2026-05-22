from google.cloud import logging_v2
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo
import re
import html

async def render(request, context):

    log_html = ""

    try:

        client = logging_v2.Client()

        agora = datetime.now(timezone.utc)
        limite = agora - timedelta(hours=4)

        limite_str = limite.strftime("%Y-%m-%dT%H:%M:%SZ")

        filtro = f'''
        resource.type="cloud_run_revision"
        severity>=ERROR
        timestamp>="{limite_str}"
        '''

        entries = client.list_entries(
            filter_=filtro,
            order_by=logging_v2.DESCENDING,
            page_size=48
        )

        log_html += "<h2>Últimos erros (Cloud Run)</h2>"

        count = 0

        tz_sp = ZoneInfo("America/Sao_Paulo")

        for entry in entries:

            if count >= 48:
                break

            count += 1

            ts = entry.timestamp.astimezone(tz_sp).strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]

            texto = ""

            if entry.payload is None:
                continue

            if isinstance(entry.payload, dict):
                texto = html.escape(str(entry.payload))
            else:
                texto = html.escape(str(entry.payload).strip())

            if not texto:
                continue

            log_html += f"""
            <div class='log-entry'>
                <div class='log-head'>
                    <span class='log-time'>{ts}</span>
                </div>
                <pre class='log-body'>{texto}</pre>
            </div>
            """

        if count == 0:
            log_html += "<p>Nenhum erro nas últimas 4 horas.</p>"

    except Exception as e:

        log_html += f"""
        <div class='log-entry'>
            <pre>Erro ao consultar logs: {html.escape(str(e))}</pre>
        </div>
        """

    body = f"""
    <h1>Logs da aplicação (Cloud Run)</h1>

    <p>
    Mostrando até <b>48 erros</b> nas últimas <b>4 horas</b>.
    </p>

    <div class="logs">
    {log_html}
    </div>
    """

    style = """

    body{
        font-family:Arial;
        padding:40px;
        background:#111;
        color:#eee;
    }

    h1{
        margin-bottom:20px;
    }

    .logs{
        display:flex;
        flex-direction:column;
        gap:20px;
    }

    .log-entry{
        background:#1b1b1b;
        border-left:5px solid #ff4d4d;
        padding:15px;
        border-radius:6px;
    }

    .log-head{
        display:flex;
        justify-content:space-between;
        margin-bottom:10px;
        font-size:14px;
    }

    .log-time{
        color:#ffd166;
        font-weight:bold;
    }

    .log-file{
        color:#7bdff2;
        font-weight:bold;
    }

    .log-body{
        white-space:pre-wrap;
        font-family:monospace;
        color:#0f0;
    }

    """

    return {
        "title": "Logs Cloud Run",
        "body": body,
        "style": style
    }
