async def render(request, context):

    db = context["db"]
    query = request.get("query", {})
    encontro_id = query.get("id")

    body = f"""
    <h1>Aqui você será redirecionado para assistir o encontro {encontro_id}</h1>
    <p>Aguarde atpe que esse procedimento seja definido em detalhes.</p>
    """

    return {
        "title": "Definir responsável pela apresentação",
        "body": body
    }
