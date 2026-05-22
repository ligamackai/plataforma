from sqlalchemy import text

async def render(request, context):

    db = context["db"]

    query = request.get("query", {})
    participante_id = query.get("id")

    if not participante_id:
        return {
            "title": "Erro",
            "body": "<h1>ID do participante não informado</h1>",
            "status": 400
        }

    result = await db.execute(
        text("""
            SELECT
                id,
                ra,
                nome,
                criado,
                atualizado
            FROM plataforma.participante
            WHERE id = :id
        """),
        {"id": int(participante_id)}
    )

    participante = result.mappings().first()

    if not participante:
        return {
            "title": "Não encontrado",
            "body": "<h1>Participante não encontrado</h1>",
            "status": 404
        }

    body = f"""
    <h1>{participante["nome"]}</h1>

    <table border="1" cellpadding="6">
        <tr><th>ID</th><td>{participante["id"]}</td></tr>
        <tr><th>RA</th><td>{participante["ra"] or ""}</td></tr>
        <tr><th>Nome</th><td>{participante["nome"]}</td></tr>
        <tr><th>Criado</th><td>{participante["criado"]}</td></tr>
        <tr><th>Atualizado</th><td>{participante["atualizado"]}</td></tr>
    </table>
    """

    return {
        "title": participante["nome"],
        "body": body
    }
