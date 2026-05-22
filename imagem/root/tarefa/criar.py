async def render(request, context):

    db = context["db"]

    body = f"""
    <h1>Criar tarefa</h1>
    <p>Aciona a função criar_tarefa (C01) no backend.</p>
    <p>Esse arquivo está no bucket no path "tarefa/criar.py"</p>
    """

    return {
        "title": "Criar tarefa",
        "body": body
    }
