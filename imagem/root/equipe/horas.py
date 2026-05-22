async def render(request, context):

    db = context["db"]
    query = request.get("query", {})
    equipe_id = query.get("id")

    body = f"""
    <h1>Atribuir horas a atividade administrativa {equipe_id}</h1>
    <p>Aciona a função vai_apresentar (D03) no backend.</p>
    <p>Esse arquivo está no bucket no path "equipe/horas.py"</p>
    """

    return {
        "title": "Atribuir horas a atividade administrativa",
        "body": body
    }
