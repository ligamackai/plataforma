async def render(request, context):

    db = context["db"]
    query = request.get("query", {})
    encontro_id = query.get("id")

    body = f"""
    <h1>Definir responsável pela apresentação {encontro_id}</h1>
    <p>Aciona a função vai_apresentar (B02) no backend.</p>
    <p>Esse arquivo está no bucket no path "encontro/apresentar.py"</p>
    """

    return {
        "title": "Definir responsável pela apresentação",
        "body": body
    }
