from sqlalchemy import text
from datetime import datetime, timezone

async def render(request, context):
    db = context["db"]
    now = datetime.now(timezone.utc)
    result = await db.execute(text("""
        SELECT 
            O.id,
            G.nome
        FROM plataforma.ocorreu O
        LEFT JOIN plataforma.grupo G
            ON O.grupo = G.id
        JOIN plataforma.semestre S
            ON O.semestre = S.id
        WHERE S.descricao =
            to_char(CURRENT_DATE, 'YYYY') || '/' ||
            CASE WHEN EXTRACT(MONTH FROM CURRENT_DATE) <= 6 THEN '1' ELSE '2' END
        ORDER BY G.nome
    """))

    rows = result.mappings().all()
    
    option = ""
    for r in rows:
        option += f"<option value='{r['id']}'>{r['nome'] or ''}</option>"
    
    body = f"""
    <h1>Agendar encontro</h1>

    <form
        id="form-encontro"
        method="post"
        action="https://plataforma-576668051133.us-central1.run.app/db/procedure/agendar_encontro"
        data-success="https://plataforma-576668051133.us-central1.run.app/encontro"
    >

        <label for="grupo">Grupo:</label><br>
        <select name="grupo" required>
            {option}
        </select><br><br>

        <label for="tema">Tema:</label><br>
        <input type="text" name="tema" maxlength="255" required><br><br>

        <label for="resumo">Resumo:</label><br>
        <textarea name="resumo" rows="4"></textarea><br><br>

        <label for="inicio">Data:</label><br>
        <input name="inicio" type="datetime-local" required><br><br>

        <label>Duração:</label><br>
        <input name="duracao_horas" type="number" min="0" max="12" value="1" required> horas
        <input name="duracao_minutos" type="number" min="0" max="59" step="5" value="0"> minutos
        <br><br>
        
        <div id="msg"></div>
        <button id="btn-enviar" type="submit">Agendar encontro</button>

    </form>"""+"""
    
    <script>

    const form = document.getElementById("form-encontro")
    const btn = document.getElementById("btn-enviar")
    const msg = document.getElementById("msg")
    
    function pgTimestamp(d){

        const pad = n => n.toString().padStart(2,'0')

        return d.getFullYear()+"-" +
               pad(d.getMonth()+1)+"-" +
               pad(d.getDate())+" "+
               pad(d.getHours())+":"+
               pad(d.getMinutes())+":"+
               pad(d.getSeconds())+
               "-03"
    }
    
    form.addEventListener("submit", async (e) => {

        e.preventDefault()

        msg.innerHTML = ""

        btn.disabled = true
        btn.className = "loading"
        btn.innerText = "Enviando..."

        const data = new FormData()

        data.append("ocorrencia", form.grupo.value)

        data.append("tema", form.tema.value)

        data.append("resumo", form.resumo.value)

        const inicioData = form.inicio.value

        const horas = parseInt(form.duracao_horas.value || 0)
        const minutos = parseInt(form.duracao_minutos.value || 0)

        const inicio = new Date(inicioData)

        const fim = new Date(inicio.getTime() + ((horas*60 + minutos) * 60000))

        data.append("inicio", pgTimestamp(inicio))
        data.append("fim", pgTimestamp(fim))

        const params = new URLSearchParams(data)

        const api = form.getAttribute("action")
        const successUrl = form.dataset.success

        try{

            const r = await fetch(api + "?" + params.toString(),{
                method:"GET"
            })
            
            const response = await r.json()

            if(response.ok){

                btn.className = "success"
                btn.innerText = "Sucesso"

                msg.innerHTML = "Agendado com sucesso"
                msg.className = "msg-success"

                setTimeout(()=>{
                    window.location = successUrl
                },800)

            }else{

                btn.disabled = false
                btn.className = "error"
                btn.innerText = "Erro"

                msg.innerHTML = response.msg?.erro || "Erro ao agendar"
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
        "title": "Agendar encontro",
        "body": body
    }
