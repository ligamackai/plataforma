async def render(request, context):

    db = context["db"]

    body = f"""
    <h1>Atribuir horas por exercer uma atividade administrativa</h1>
    <p>Aciona a função horas_cargo (D03) no backend.</p>
    <p>Esse arquivo está no bucket no path "cargo/horas.py"</p>
    """

    return {
        "title": "Atribuir horas por exercer uma atividade administrativa",
        "body": body
    }
