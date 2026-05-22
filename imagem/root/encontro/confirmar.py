async def render(request, context):

    db = context["db"]
    query = request.get("query", {})
    encontro_id = query.get("id")

    body = f"""
    <h1>Confirmar horas pela apresentação do encontro {encontro_id}</h1>
    <p>Aciona a função confirmar_apresentacao (B03) no backend.</p>
    <p>Esse arquivo está no bucket no path "encontro/horas.py"</p>
    """

    return {
        "title": "Confirmar horas pela apresentação",
        "body": body
    }
