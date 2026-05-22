async def render(request, context):

    db = context["db"]
    query = request.get("query", {})
    tarefa_id = query.get("id")

    body = f"""
    <h1>Inscrever participante na tarefa {tarefa_id}</h1>
    <p>Aciona a função inscrever_tarefa (C02) no backend.</p>
    <p>Esse arquivo está no bucket no path "tarefa/inscrever.py"</p>
    """

    return {
        "title": "Inscrever participante em tarefa",
        "body": body
    }
