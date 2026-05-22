def render(request_data, context):
    user_id = context["request"].state.participante_id

    if user_id:
        return {
            "redirect": "/logout"
        }

    body = """
        
<h1>Login</h1>

<div id="links">
    <button onclick="location.href='/cadastrar'">Criar conta</button>
    <button onclick="location.href='/recuperar'">Esqueci minha senha</button>
</div>

<form id='login' onsubmit="return logar(this)">
    <label for='ra'>Digite o seu RA:</label>
    <input type='text' name='ra'>

    <label for='senha'>Digite sua senha:</label>
    <input type='password' name='senha'>

    <p id='login-mensagem'></p>

    <input type='submit' value='Fazer Login'>
</form>

<script>
async function logar(btn){
    event.preventDefault()

    const msg = document.getElementById("login-mensagem")

    const ra = document.querySelector("input[name='ra']").value.trim()
    const senha = document.querySelector("input[name='senha']").value

    // validação mínima
    if(ra.length < 8 || senha.length < 1){
        msg.innerText = "Preencha corretamente os campos."
        msg.style.color = "red"
        return false
    }

    btn.disabled = true

    msg.innerText = "Aguarde, estamos realizando o login..."
    msg.style.color = "#b58900"

    try{

        const params = new URLSearchParams({
            ra: ra,
            senha: senha
        })

        const resp = await fetch("/realizar/login/",{
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

            // redireciona após login
            setTimeout(()=>{
                window.location.href = "/"
            },1000)

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

#login-mensagem {
    margin-top: 12px;
}

#links {
    max-width: 400px;
    margin-top: 20px;
    display: flex;
    gap: 10px;
    margin-bottom: 8px;
}

#links button {
    flex: 1;
    padding: 8px;
    background-color: #2a2f36;
    border: 1px solid #444;
    border-radius: 6px;
    color: #ddd;
    cursor: pointer;
    transition: 0.2s;
}

#links button:hover {
    background-color: #3a4048;
}

    """

    return {
        'title': 'Login',
        'body': body,
        'style': style
    }
