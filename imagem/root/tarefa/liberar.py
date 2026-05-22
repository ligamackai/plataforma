async def render(request, context):

    db = context["db"]
    query = request.get("query", {})
    tarefa_id = query.get("id")

    body = f"""
    <h1>Cancelar execução da tarefa {tarefa_id}</h1>
    <p>Aciona a função cancelar_execucao (C04) no backend.</p>
    <p>Esse arquivo está no bucket no path "tarefa/liberar.py"</p>
    """

    return {
        "title": "Cancelar execução de tarefa",
        "body": body
    }
