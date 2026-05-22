async def render(request, context):

    db = context["db"]

    body = f"""
    <h1>Encerrar atividade administrativa</h1>
    <p>Aciona a função encerrar_cargo (D02) no backend.</p>
    <p>Esse arquivo está no bucket no path "cargo/encerrar.py"</p>
    """

    return {
        "title": "Encerrar atividade administrativa",
        "body": body
    }
