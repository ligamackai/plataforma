async def render(request, context):

    db = context["db"]
    query = request.get("query", {})
    tarefa_id = query.get("id")

    body = f"""
    <h1>Cancelar tarefa {tarefa_id}</h1>
    <p>Aciona a função cancelar_tarefa (C05) no backend.</p>
    <p>Esse arquivo está no bucket no path "tarefa/cancelar.py"</p>
    """

    return {
        "title": "Cancelar tarefa",
        "body": body
    }
