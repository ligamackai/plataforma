from sqlalchemy import text

async def render(request, context):

    db = context["db"]

    query = request.get("query", {})
    encontro_id = query.get("id")

    if not encontro_id:
        return {
            "title": "Erro",
            "body": "<h1>ID do encontro não informado</h1>",
            "status": 400
        }

    result = await db.execute(
        text("""
            SELECT
                e.*,
                g.nome AS grupo_nome
            FROM plataforma.encontro e
            JOIN plataforma.ocorreu o ON o.id = e.ocorrencia
            JOIN plataforma.grupo g ON g.id = o.grupo
            WHERE e.id = :id
        """),
        {"id": int(encontro_id)}
    )

    encontro = result.mappings().first()

    if not encontro:
        return {
            "title": "Não encontrado",
            "body": "<h1>Encontro não encontrado</h1>",
            "status": 404
        }

    body = f"""
    <h1>{encontro["tema"]}</h1>

    <a href="/encontro/{encontro_id}/assistir" class="side-btn">
	Assistir
    </a>
    <a href="/encontro/{encontro_id}/apresentar" class="side-btn">
	+ Inscrever para apresentar
    </a>
    <a href="/encontro/{encontro_id}/liberar" class="side-btn">
	- Cancelar inscrição
    </a>
    <a href="/encontro/{encontro_id}/confirmar" class="side-btn">
	Confirmar apresentação
    </a>
    <a href="/encontro/{encontro_id}/cancelar" class="side-btn">
	- Cancelar encontro
    </a>
    
    <br><br>

    <table border="1" cellpadding="6">
        <tr><th>ID</th><td>{encontro["id"]}</td></tr>
        <tr><th>Grupo</th><td>{encontro["grupo_nome"]}</td></tr>
        <tr><th>Início</th><td>{encontro["inicio"]}</td></tr>
        <tr><th>Fim</th><td>{encontro["fim"]}</td></tr>
        <tr><th>Válido</th><td>{encontro["valido"]}</td></tr>
        <tr><th>Resumo</th><td>{encontro["resumo"] or ""}</td></tr>
        <tr><th>Vídeo</th><td>{encontro["video"] or ""}</td></tr>
    </table>
    """

    return {
        "title": encontro["tema"],
        "body": body
    }
