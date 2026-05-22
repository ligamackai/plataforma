from sqlalchemy import text

async def render(request, context):

    db = context["db"]

    query = request.get("query", {})
    equipe_id = query.get("id")

    result = await db.execute(
        text("""
            SELECT
                c.id,
                p.nome AS participante,
                tc.nome AS tipo,
                tc.id AS tipo_id,
                c.inicio,
                c.fim
            FROM plataforma.cargo c
            JOIN plataforma.participante p ON p.id = c.participante
            JOIN plataforma.tipo_cargo tc ON tc.id = c.tipo
            WHERE c.id = :id
        """),
        {"id": int(equipe_id)}
    )

    equipe = result.mappings().first()

    if not equipe:
        return {
            "title": "Não encontrado",
            "body": "<h1>Grupo não encontrado</h1>",
            "status": 404
        }

    body = f"""
    <h1>{equipe["participante"]}</h1>

    <a href="/equipe/{equipe_id}/encerrar" class="side-btn">
	    - Encerrar participação
    </a>
    <a href="/equipe/{equipe_id}/horas" class="side-btn">
	    + Atribuir horas
    </a>

    <br><br>

    <table border="1" cellpadding="6">
        <tr><th>ID</th><td>{equipe["id"]}</td></tr>
        <tr><th>Tipo</th><td>{equipe["tipo"]}</td></tr>
        <tr><th>ID do tipo</th><td>{equipe["tipo_id"]}</td></tr>
        <tr><th>Início</th><td>{equipe["inicio"]}</td></tr>
        <tr><th>Fim</th><td>{equipe["fim"]}</td></tr>
    </table>
    """

    return {
        "title": equipe["participante"],
        "body": body
    }
