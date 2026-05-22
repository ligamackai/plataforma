def render(request_data, context):
    user_id = context["request"].state.participante_id

    if user_id:
        return {
            "redirect": "/"
        }

    body = """
        
<h1>Recuperar senha</h1>

<form id='recuperar' onsubmit="return recuperar(this)">
    <label for='ra'>Digite o seu RA:</label>
    <input type='text' name='ra'>

    <div id='instrucao'>
        <p>Digite seu RA e clique em <b>Enviar</b> para receber um código no e-mail institucional.</p>
        <p><i>SEU-RA@mackenzista.com.br</i></p>
        <p>O código tem validade de <b>20 minutos</b>.</p>
    </div>

    <label for='codigo'>Código recebido por e-mail:</label>
    <div id='codigo'>
        <button onclick='enviarCodigo(this)'>Enviar</button>
        <input type='text' name='codigo'>
    </div>

    <p id='email-mensagem'></p>

    <label for='senha'>Digite sua nova senha:</label>
    <input type='password' name='senha'>

    <label for='senha_confirma'>Digite novamente:</label>
    <input type='password' name='senha_confirma'>

    <p id='recuperar-mensagem'></p>

    <input type="submit" value="Atualizar senha">
</form>

<script>
async function enviarCodigo(btn){

    const msg = document.getElementById("email-mensagem")
    const ra = document.querySelector("input[name='ra']").value

    if(!ra){
        msg.innerText = "Digite seu RA primeiro."
        msg.style.color = "red"
        return
    }

    btn.disabled = true
    msg.innerText = "Enviando código..."
    msg.style.color = "#b58900"

    try{
        const resp = await fetch(`/send/code/?to=${encodeURIComponent(ra)}`,{
            method: "GET",
            credentials: "same-origin"
        })

        const data = await resp.json()

        msg.innerText = data.message
        msg.style.color = data.status === "ok" ? "lightgreen" : "red"

    }catch(e){
        msg.innerText = "Erro ao enviar código."
        msg.style.color = "red"
    }finally{
        btn.disabled = false
    }
}

async function recuperar(btn){
    event.preventDefault()

    const msg = document.getElementById("recuperar-mensagem")

    const ra = document.querySelector("input[name='ra']").value.trim()
    const codigo = document.querySelector("input[name='codigo']").value.trim()
    const senha = document.querySelector("input[name='senha']").value
    const senha_confirma = document.querySelector("input[name='senha_confirma']").value

    if(ra.length < 8 || codigo.length < 8 || senha.length < 8){
        msg.innerText = "Todos os campos devem ter pelo menos 8 caracteres."
        msg.style.color = "red"
        return false
    }

    if(senha !== senha_confirma){
        msg.innerText = "As senhas não são iguais."
        msg.style.color = "red"
        return false
    }

    btn.disabled = true
    msg.innerText = "Atualizando senha..."
    msg.style.color = "#b58900"

    try{

        const params = new URLSearchParams({
            ra: ra,
            codigo: codigo,
            senha: senha
        })

        const resp = await fetch("/realizar/recuperar-senha/",{
            method: "POST",
            credentials: "same-origin",
            headers:{
                "Content-Type":"application/x-www-form-urlencoded"
            },
            body: params.toString()
        })

        const data = await resp.json()

        msg.innerText = data.message
        msg.style.color = data.status === "ok" ? "lightgreen" : "red"

        if(data.status === "ok"){
            setTimeout(()=>{
                window.location.href = "/login"
            },2000)
        }

    }catch(e){
        msg.innerText = "Erro ao comunicar com o servidor."
        msg.style.color = "red"
    }finally{
        btn.disabled = false
    }

    return false
}
</script>

    """

    style = """
input[type="submit"] {
    background-color: lightgreen;
    font-weight: bold;
    cursor: pointer;
}

#instrucao {
    margin: 8px;
    padding: 8px;
    border: solid 2px orange;
}

#codigo {
    display:flex;
    align-items: center;
}

#codigo button {    
    font-weight:bold;
    height: fit-content;
}

#codigo input {    
    margin: 0
}

#email-mensagem {
    margin-bottom: 20px;
}
    """

    return {
        'title': 'Recuperar senha',
        'body': body,
        'style': style
    }
