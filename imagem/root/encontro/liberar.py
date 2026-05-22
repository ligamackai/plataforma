async def render(request, context):

    db = context["db"]
    query = request.get("query", {})
    encontro_id = query.get("id")

    body = f"""
    <h1>Cancelar inscrição na apresentação do encontro {encontro_id}</h1>
    <p>Aciona a função cancelar_apresentar (B02B) no backend.</p>
    <p>Esse arquivo está no bucket no path "encontro/liberar.py"</p>
    """

    return {
        "title": "Cancelar inscrição em apresentação",
        "body": body
    }
