async def render(request, context):

    db = context["db"]

    body = f"""
    <h1>Atribuir cargo a um participante</h1>
    <p>Aciona a função adicionar_cargo (D01B) no backend.</p>
    <p>Esse arquivo está no bucket no path "cargo/atribuir.py"</p>
    """

    return {
        "title": "Atribuir cargo a um participante",
        "body": body
    }
