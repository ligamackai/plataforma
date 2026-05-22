async def render(request, context):

    db = context["db"]

    body = f"""
    <h1>Criar novo grupo</h1>
    <p>Aciona a função criar_grupo (A04) no backend.</p>
    <p>Esse arquivo está no bucket no path "grupo/novo.py"</p>
    """

    return {
        "title": "Criar novo grupo",
        "body": body
    }
