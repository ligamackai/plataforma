from sqlalchemy import text

async def render(request, context):

    db = context["db"]

    # -----------------------------------------------------------
    # 1. Buscar grupos que NÃO estão ativos no semestre atual
    # -----------------------------------------------------------
    result = await db.execute(text("""
        SELECT
            G.id,
            G.nome,
            G.tipo
        FROM plataforma.grupo G
        WHERE G.id NOT IN (
            SELECT O.grupo
            FROM plataforma.ocorreu O
            JOIN plataforma.semestre S
                ON O.semestre = S.id
            WHERE S.descricao =
                to_char(CURRENT_DATE, 'YYYY') || '/' ||
                CASE WHEN EXTRACT(MONTH FROM CURRENT_DATE) <= 6 THEN '1' ELSE '2' END
        )
        ORDER BY G.nome
    """))

    rows = result.mappings().all()

    option = ""
    for r in rows:
        option += f"<option value='{r['id']}'>{r['nome'] or ''} ({r['tipo'] or 'sem tipo'})</option>"

    # -----------------------------------------------------------
    # 2. Buscar semestre atual para exibir
    # -----------------------------------------------------------
    semestre_result = await db.execute(text("""
        SELECT id, descricao
        FROM plataforma.semestre
        WHERE descricao =
            to_char(CURRENT_DATE, 'YYYY') || '/' ||
            CASE WHEN EXTRACT(MONTH FROM CURRENT_DATE) <= 6 THEN '1' ELSE '2' END
        LIMIT 1
    """))
    semestre_atual = semestre_result.mappings().first()
    semestre_label = semestre_atual["descricao"] if semestre_atual else "semestre atual"
    semestre_id = semestre_atual["id"] if semestre_atual else ""

    # -----------------------------------------------------------
    # 3. Montar HTML
    # -----------------------------------------------------------
    body = f"""
    <h1>Ativar grupo no semestre atual</h1>

    <p style="margin-bottom:20px;color:#aaa;">
        Semestre atual: <strong>{semestre_label}</strong>
    </p>

    <form
        id="form-ativar"
        method="post"
        action="https://plataforma-576668051133.us-central1.run.app/db/procedure/criar_ocorrencia"
        data-success="https://plataforma-576668051133.us-central1.run.app"
    >

        <input type="hidden" name="semestre" value="{semestre_id}">

        <label for="grupo">Grupo:</label><br>
        <select name="grupo" required>
            <option value="">Selecione um grupo</option>
            {option}
        </select><br><br>

        <div id="msg"></div>
        <button id="btn-enviar" type="submit">Ativar grupo</button>

    </form>
    """

    # -----------------------------------------------------------
    # 4. JavaScript (mesmo padrão do agendar.py)
    # -----------------------------------------------------------
    body += """
    <script>

    const form = document.getElementById("form-ativar")
    const btn = document.getElementById("btn-enviar")
    const msg = document.getElementById("msg")

    form.addEventListener("submit", async (e) => {

        e.preventDefault()

        msg.innerHTML = ""

        btn.disabled = true
        btn.className = "loading"
        btn.innerText = "Enviando..."

        const data = new FormData()

        data.append("grupo", form.grupo.value)
        data.append("semestre", form.semestre.value)

        const params = new URLSearchParams(data)

        const api = form.getAttribute("action")
        const successUrl = form.dataset.success

        try{

            const r = await fetch(api + "?" + params.toString(), {
                method:"GET"
            })

            const response = await r.json()

            if(response.ok){

                btn.className = "success"
                btn.innerText = "Sucesso"

                msg.innerHTML = "Grupo ativado com sucesso!"
                msg.className = "msg-success"

                setTimeout(()=>{
                    window.location = successUrl
                }, 800)

            }else{

                btn.disabled = false
                btn.className = "error"
                btn.innerText = "Erro"

                const erroMsg = response.msg?.erro || response.msg || "Erro ao ativar grupo"
                msg.innerHTML = erroMsg
                msg.className = "msg-error"

            }

        }catch(err){

            btn.disabled = false
            btn.className = "error"
            btn.innerText = "Erro"

            msg.innerHTML = "Erro de conexão"
            msg.className = "msg-error"

        }

    })

    </script>
    """

    return {
        "title": "Ativar grupo no semestre atual",
        "body": body
    }
