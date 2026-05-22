async def render(request, context):

    db = context["db"]
    query = request.get("query", {})
    encontro_id = query.get("id")

    body = f"""
    <h1>Cancelar encontro {encontro_id}</h1>
    <p>Aciona a função cancelar_encontro (B05) no backend.</p>
    <p>Esse arquivo está no bucket no path "encontro/cancelar.py"</p>
    """

    return {
        "title": "Cancelar encontro",
        "body": body
    }
