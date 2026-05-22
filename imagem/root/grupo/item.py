from sqlalchemy import text

async def render(request, context):

    db = context["db"]

    query = request.get("query", {})
    grupo_id = query.get("id")

    if not grupo_id:
        return {
            "title": "Erro",
            "body": "<h1>ID do grupo não informado</h1>",
            "status": 400
        }

    result = await db.execute(
        text("""
            SELECT
                id,
                nome,
                tipo,
                descricao,
                criado,
                atualizado
            FROM plataforma.grupo
            WHERE id = :id
        """),
        {"id": int(grupo_id)}
    )

    grupo = result.mappings().first()

    if not grupo:
        return {
            "title": "Não encontrado",
            "body": "<h1>Grupo não encontrado</h1>",
            "status": 404
        }

    body = f"""
    <h1>{grupo["nome"]}</h1>

    <a href="/grupo/{grupo_id}/encontro" class="side-btn">
	    Encontros
    </a>
    <a href="/grupo/{grupo_id}/tarefa" class="side-btn">
	    Tarefas
    </a>

    <br><br>

    <table border="1" cellpadding="6">
        <tr><th>ID</th><td>{grupo["id"]}</td></tr>
        <tr><th>Tipo</th><td>{grupo["tipo"]}</td></tr>
        <tr><th>Descrição</th><td>{grupo["descricao"] or ""}</td></tr>
        <tr><th>Criado</th><td>{grupo["criado"]}</td></tr>
        <tr><th>Atualizado</th><td>{grupo["atualizado"]}</td></tr>
    </table>
    """

    return {
        "title": grupo["nome"],
        "body": body
    }
