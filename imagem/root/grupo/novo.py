async def render(request, context):

    body = """
    <h1>Criar novo grupo</h1>

    <form
        id="form-grupo"
        method="post"
        action="https://plataforma-576668051133.us-central1.run.app/db/procedure/criar_grupo"
        data-success="https://plataforma-576668051133.us-central1.run.app/"
    >

        <label for="nome">Nome do grupo:</label><br>
        <input type="text" name="nome" maxlength="255" required><br><br>

        <label for="tipo">Tipo:</label><br>
        <select name="tipo" required>
            <option value="estudo">Estudo</option>
            <option value="trabalho">Trabalho</option>
            <option value="pesquisa">Pesquisa</option>
        </select><br><br>

        <label for="descricao">Descrição:</label><br>
        <textarea name="descricao" rows="4"></textarea><br><br>

        <div id="msg"></div>
        <button id="btn-enviar" type="submit">Criar grupo</button>

    </form>

    <script>

    const form = document.getElementById("form-grupo")
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
        data.append("tipo", form.tipo.value)
        data.append("descricao", form.descricao.value)

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

                msg.innerHTML = "Grupo criado com sucesso"
                msg.className = "msg-success"

                setTimeout(()=>{
                    window.location = successUrl
                },800)

            }else{

                btn.disabled = false
                btn.className = "error"
                btn.innerText = "Erro"

                msg.innerHTML = response.msg?.erro || "Erro ao criar grupo"
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
        "title": "Criar novo grupo",
        "body": body
    }
