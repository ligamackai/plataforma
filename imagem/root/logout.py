from sqlalchemy import text
from zoneinfo import ZoneInfo

async def render(request_data, context):

    user_id = context["request"].state.participante_id

    if not user_id:
        return {
            "redirect": "/login"
        }

    db = context["db"]

    ra = ""
    nome = ""
    criado = ""

    row = (
        await db.execute(
            text("""
            SELECT ra, nome, criado
            FROM plataforma.participante
            WHERE id = :id
            """),
            {"id": user_id}
        )
    ).mappings().first()

    if row:
        ra = row["ra"]
        nome = row["nome"]

        criado_dt = row["criado"]

        if criado_dt:
            criado = criado_dt.astimezone(
                ZoneInfo("America/Sao_Paulo")
            ).strftime("%d/%m/%Y %H:%M:%S")

    body = f"""
        
<h1>Meus dados</h1>

<form method="GET" action="/realizar/logout/">

    <label>ID de usuário:</label>
    <input type='text' disabled value='{user_id}'>

    <label>Meu RA:</label>
    <input type='text' disabled value='{ra}'>

    <label>Meu nome:</label>
    <input type='text' disabled value='{nome}'>

    <label>Cadastrado em:</label>
    <input type='text' disabled value='{criado}'>

    <input type='submit' value='Sair / Logout'>

</form>

    """

    style = """
input[type="submit"] {
    background-color: #f9baba;
    font-weight: bold;
    border: solid 1px red;
    cursor: pointer;
}

input[disabled] {
    color: black;
}
    """

    return {
        'title': 'Login',
        'body': body,
        'style': style
    }
