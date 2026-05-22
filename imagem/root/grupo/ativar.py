async def render(request, context):

    db = context["db"]

    body = f"""
    <h1>Ativar grupo no semestre atual</h1>
    <p>Aciona a função criar_ocorrencia (A05) no backend.</p>
    <p>Esse arquivo está no bucket no path "grupo/ativar.py"</p>
    """

    return {
        "title": "Ativar grupo no semestre atual",
        "body": body
    }
