from datetime import datetime, timezone

async def render(request, context):
    body = """
    <h1>Adicionar atividade administrativa</h1>

    <form
        id="form-cargo"
        action="https://plataforma-576668051133.us-central1.run.app/db/procedure/adicionar_tipo_cargo"
        data-success="https://plataforma-576668051133.us-central1.run.app/equipe"
    >

        <label for="nome">Nome:</label><br>
        <input type="text" name="nome" maxlength="255" required><br><br>

        <label for="descricao">Descrição:</label><br>
        <textarea name="descricao" rows="4"></textarea><br><br>

        <label for="horas">Horas complementares:</label><br>
        <input name="horas" type="number" min="0" max="50">
        <br><br>
        
        <div id="msg"></div>
        <button id="btn-enviar" type="submit">Agendar encontro</button>

    </form>
    
    <script>

    const form = document.getElementById("form-cargo")
    const btn = document.getElementById("btn-enviar")
    const msg = document.getElementById("msg")
    
    form.addEventListener("submit", async (e) => {

        e.preventDefault()

        msg.innerHTML = ""

        btn.disabled = true
        btn.className = "loading"
        btn.innerText = "Enviando..."

        const data = new FormData()

        data.append("nome", form.nome.value)

        data.append("descricao", form.descricao.value)

        data.append("horas", form.horas.value)

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

                msg.innerHTML = "Cargo criado com sucesso"
                msg.className = "msg-success"

                setTimeout(()=>{
                    window.location = successUrl
                },800)

            }else{

                btn.disabled = false
                btn.className = "error"
                btn.innerText = "Erro"

                msg.innerHTML = response.msg?.erro || "Erro ao criar cargo"
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
        "title": "Adicionar atividade administrativa",
        "body": body
    }
