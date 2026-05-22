def render(request, context):
    user_id = context["request"].state.participante_id

    if user_id:
        return {
            "redirect": "/logout"
        }

    body = """
        
<h1>Cadastrar na Plataforma</h1>
<form id='cadastro' onsubmit="return cadastrar(this)">
    <label for='ra'>Digite o seu RA:</label>
    <input type='text' name='ra'>
    <div id='instrucao'>
        <p>Após digitar seu RA acima clique em <b>Enviar</b> abaixo, e um código será enviado para seu e-mail mackenzista:</p>
        <p><i>SEU-RA@mackenzista.br<i></p>
        <p>Copie o código recebido por email e cole abaixo ao lado do botão enviar.</p>
        <p>O código tem validade de <b>20 minutos</b>. Sendo assim, deve-se terminar o cadastro antes de sua expiração ou solicitar outro código caso esse tempo tenha passado.</p>
    </div>
    <label for='codigo'>Código recebido por e-mail:</label>
    <div id='codigo'>
        <button onclick='enviarCodigo(this)'>Enviar</button>
        <input type='text' name='codigo'>
    </div>
    <p id='email-mensagem'></p>
    <label for='nome'>Digite seu nome completo:</label>
    <input type='text' name='nome'>
    <label for='senha'>Digite sua senha:</label>
    <input type='password' name='senha'>
    <label for='senha_confirma'>Digite sua senha novamente:</label>
    <input type='password' name='senha_confirma'>
    <p id='cadastro-mensagem'></p>
    <input type="submit" value="Cadastrar">
<form>

<script>
async function enviarCodigo(btn){

    const msg = document.getElementById("email-mensagem")
    const ra = document.querySelector("input[name='ra']").value

    if(!ra){
        msg.innerText = "Digite seu RA primeiro."
        msg.style.color = "red"
        return
    }

    // trava botão
    btn.disabled = true

    // mensagem de espera
    msg.innerText = "Aguarde que estamos enviando o e-mail..."
    msg.style.color = "#b58900"   // amarelo escuro

    try{

        const resp = await fetch(`/send/code/?to=${encodeURIComponent(ra)}`,{
            method: "GET",
            credentials: "same-origin"
        })

        const data = await resp.json()

        msg.innerText = data.message

        if(data.status === "ok"){
            msg.style.color = "lightgreen"
        }else{
            msg.style.color = "red"
        }

    }catch(e){

        msg.innerText = "Erro ao comunicar com o servidor."
        msg.style.color = "red"

    }finally{

        // libera botão novamente
        btn.disabled = false

    }
}

async function cadastrar(btn){
    event.preventDefault()

    const msg = document.getElementById("cadastro-mensagem")

    const ra = document.querySelector("input[name='ra']").value.trim()
    const codigo = document.querySelector("input[name='codigo']").value.trim()
    const nome = document.querySelector("input[name='nome']").value.trim()
    const senha = document.querySelector("input[name='senha']").value
    const senha_confirma = document.querySelector("input[name='senha_confirma']").value

    // valida tamanho mínimo
    if(ra.length < 8 || codigo.length < 8 || nome.length < 8 || senha.length < 8){
        msg.innerText = "Todos os campos devem ter pelo menos 8 caracteres."
        msg.style.color = "red"
        return false
    }

    // valida senha
    if(senha !== senha_confirma){
        msg.innerText = "As senhas não são iguais."
        msg.style.color = "red"
        return false
    }

    btn.disabled = true

    msg.innerText = "Aguarde, estamos realizando o cadastro..."
    msg.style.color = "#b58900"

    try{

        const params = new URLSearchParams({
            ra: ra,
            codigo: codigo,
            nome: nome,
            senha: senha
        })

        const resp = await fetch("/realizar/cadastro/",{
            method: "POST",
            credentials: "same-origin",
            headers:{
                "Content-Type":"application/x-www-form-urlencoded"
            },
            body: params.toString()
        })

        const data = await resp.json()

        msg.innerText = data.message

        if(data.status === "ok"){
            msg.style.color = "lightgreen"

            setTimeout(()=>{
                window.location.href = "/"
            },5000)

        }else{
            msg.style.color = "red"
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
    border: solid 2px red;
}
#instrucao p {
    margin-bottom:4px;
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
    margin-bottom: 32px;
}

    """
    return {
        'title': 'Cadastrar',
        'body': body,
        'style': style
    }
