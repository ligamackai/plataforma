async def render(request, context):

    db = context["db"]
    query = request.get("query", {})
    tarefa_id = query.get("id")

    body = f"""
    <h1>Confirmar execução da tarefa {tarefa_id}</h1>
    <p>Aciona a função confirmar_execucao (C03) no backend.</p>
    <p>Esse arquivo está no bucket no path "tarefa/confirmar.py"</p>
    """

    return {
        "title": "Confirmar execução de tarefa",
        "body": body
    }
