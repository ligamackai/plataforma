from sqlalchemy import text
from typing import Optional


async def verificar_permissao(
    context: dict,
    p_permissao: str,
    p_grupo: Optional[int] = None,
) -> bool:
    """
    Verifica se o usuário logado tem uma determinada permissão.
    
    context: dict com 'db' (AsyncSession) e 'request' (Request do FastAPI)
    p_permissao: Nome da permissão (string, ex: 'criar_encontro')
    p_grupo: ID do grupo (opcional, para abrangência restrita)
    
    Retorna True se permitido, False caso contrário.
    """
    db = context["db"]
    participante_id = context["request"].state.participante_id

    if not participante_id:
        return False

    try:
        if p_grupo is not None:
            await db.execute(
                text("""
                    SELECT plataforma.verificar_permissao(
                        :p_participante, :p_permissao, :p_grupo
                    )
                """),
                {
                    "p_participante": participante_id,
                    "p_permissao": p_permissao,
                    "p_grupo": p_grupo,
                }
            )
        else:
            await db.execute(
                text("""
                    SELECT plataforma.verificar_permissao(
                        :p_participante, :p_permissao
                    )
                """),
                {
                    "p_participante": participante_id,
                    "p_permissao": p_permissao,
                }
            )
        return True
    except Exception:
        await db.rollback()
        return False
