import base64
import secrets
from fastapi import Request
from sqlalchemy import text

from db import SessionLocal


def int_to_base64(n: int) -> str:
    length = (n.bit_length() + 7) // 8 or 1
    return base64.urlsafe_b64encode(n.to_bytes(length, "big")).decode().rstrip("=")


def base64_to_int(s: str) -> int:
    padding = '=' * (-len(s) % 4)
    return int.from_bytes(base64.urlsafe_b64decode(s + padding), "big")


def random_base64(length: int = 64) -> str:
    byte_len = int(length * 3 / 4) + 3
    token = base64.urlsafe_b64encode(secrets.token_bytes(byte_len)).decode()
    return token.rstrip("=")[:length]


def decode_token(token: str):
    a, b = token.split("@", 1)
    return base64_to_int(a), b


async def session_middleware(request: Request, call_next):

    session_cookie = request.cookies.get("session")

    dispositivo_id = None
    participante_id = None
    codigo = None

    async with SessionLocal() as db:

        if session_cookie:

            try:
                dispositivo_id, codigo = decode_token(session_cookie)

                row = (
                    await db.execute(
                        text("""
                        SELECT d.id, s.participante
                        FROM plataforma.dispositivo d
                        LEFT JOIN plataforma.sessao s
                          ON s.dispositivo = d.id
                        WHERE d.id=:id AND d.codigo=:codigo
                        """),
                        {"id": dispositivo_id, "codigo": codigo}
                    )
                ).mappings().first()

                if row:
                    participante_id = row["participante"]
                else:
                    dispositivo_id = None

            except Exception:
                dispositivo_id = None

        if dispositivo_id is None:

            codigo = random_base64(64)

            dispositivo_id = (
                await db.execute(
                    text("""
                    INSERT INTO plataforma.dispositivo(codigo)
                    VALUES(:codigo)
                    RETURNING id
                    """),
                    {"codigo": codigo}
                )
            ).scalar()

            await db.commit()

            session_cookie = f"{int_to_base64(dispositivo_id)}@{codigo}"

        # state nativo do FastAPI
        request.state.dispositivo_id = dispositivo_id
        request.state.participante_id = participante_id

        await db.execute(
            text("""
            INSERT INTO plataforma.acesso
            (dispositivo, participante, url)
            VALUES (:d, :p, :u)
            """),
            {
                "d": dispositivo_id,
                "p": participante_id,
                "u": str(request.url)
            }
        )

        await db.commit()

    response = await call_next(request)

    response.set_cookie(
        "session",
        session_cookie,
        httponly=True,
        secure=True,
        samesite="Lax",
        max_age=60*60*24*365*10
    )

    return response
