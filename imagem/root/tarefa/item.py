from sqlalchemy import text

async def render(request, context):

    db = context["db"]

    query = request.get("query", {})
    tarefa_id = query.get("id")

    if not tarefa_id:
        return {
            "title": "Erro",
            "body": "<h1>ID da tarefa não informado</h1>",
            "status": 400
        }

    result = await db.execute(
        text("""
            SELECT
                t.*,
                g.nome AS grupo_nome
            FROM plataforma.tarefa t
            JOIN plataforma.ocorreu o ON o.id = t.ocorrencia
            JOIN plataforma.grupo g ON g.id = o.grupo
            WHERE t.id = :id
        """),
        {"id": int(tarefa_id)}
    )

    tarefa = result.mappings().first()

    if not tarefa:
        return {
            "title": "Não encontrado",
            "body": "<h1>Tarefa não encontrada</h1>",
            "status": 404
        }

    body = f"""
    <h1>{tarefa["tema"]}</h1>
    <a class="side-btn" href="/tarefa/{tarefa_id}/inscrever">
        + Me inscrever
    </a>
    <a class="side-btn" href="/tarefa/{tarefa_id}/liberar">
        - Cancelar inscrição
    </a>
    <a class="side-btn" href="/tarefa/{tarefa_id}/confirmar">
        Confirmar execução
    </a>
    <a class="side-btn" href="/tarefa/{tarefa_id}/cancelar">
        - Cancelar tarefa
    </a>
    <br><br>
    <table border="1" cellpadding="6">
        <tr><th>ID</th><td>{tarefa["id"]}</td></tr>
        <tr><th>Grupo</th><td>{tarefa["grupo_nome"]}</td></tr>
        <tr><th>Horas</th><td>{tarefa["horas"]}</td></tr>
        <tr><th>Réplicas</th><td>{tarefa["replicas"]}</td></tr>
        <tr><th>Início</th><td>{tarefa["inicio"]}</td></tr>
        <tr><th>Prazo</th><td>{tarefa["prazo"] or ""}</td></tr>
        <tr><th>Válido</th><td>{tarefa["valido"]}</td></tr>
        <tr><th>Descrição</th><td>{tarefa["descricao"] or ""}</td></tr>
        <tr><th>Vídeo</th><td>{tarefa["video"] or ""}</td></tr>
    </table>
    """

    return {
        "title": tarefa["tema"],
        "body": body
    }
