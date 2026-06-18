import os
import re
from typing import Optional, AsyncGenerator, List, Any, Dict
import json
from urllib.request import urlopen
import psycopg2
import asyncio
from concurrent.futures import ThreadPoolExecutor
from urllib.parse import quote
from fastapi import FastAPI, Depends, Request, Form
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import (
    create_async_engine,
    async_sessionmaker,
    AsyncSession,
)
from sqlalchemy import text
from datetime import datetime, date, time

from middleware import session_middleware
from router import dynamic_router, init_router
from db import SessionLocal, engine, get_session, DB_SCHEMA, DB_NAME, DB_USER, DB_PASSWORD, DB_HOST, DB_PORT
import smtplib
from email.message import EmailMessage
import secrets
import hashlib

emails_aceitos = ["mackenzista.com.br", "mackenzie.br"]

# ============================================================
# Helpers
# ============================================================

def validate_identifier(name: str) -> str:
    """Protege nomes de tabelas/functions/procedures"""
    if not re.match(r"^[A-Za-z_][A-Za-z0-9_]*$", name):
        raise ValueError(f"Identificador inválido: {name}")
    return name


def success(data: Any) -> Dict[str, Any]:
    return {"ok": True, "data": data}


def failure(msg: str) -> Dict[str, Any]:
    return {"ok": False, "msg": msg}

def gerar_codigo(tamanho=8):
    caracteres = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
    return "".join(secrets.choice(caracteres) for _ in range(tamanho))

def hash_senha(senha: str):

    salt = os.urandom(16)

    key = hashlib.pbkdf2_hmac(
        "sha256",
        senha.encode(),
        salt,
        200000
    )

    return salt.hex() + ":" + key.hex()

def verificar_senha(senha_digitada: str, senha_db: str):

    salt_hex, hash_hex = senha_db.split(":")

    salt = bytes.fromhex(salt_hex)

    key = hashlib.pbkdf2_hmac(
        "sha256",
        senha_digitada.encode(),
        salt,
        200000
    )

    return key.hex() == hash_hex

async def verificar_permissao(
    session: AsyncSession,
    p_participante: int,
    p_permissao: int,
    p_grupo: Optional[int] = None,
) -> bool:
    try:
        if p_grupo is not None:
            await session.execute(
                text(f'SELECT "{DB_SCHEMA}".verificar_permissao(:p, :perm, :g)'),
                {"p": p_participante, "perm": p_permissao, "g": p_grupo}
            )
        else:
            await session.execute(
                text(f'SELECT "{DB_SCHEMA}".verificar_permissao(:p, :perm)'),
                {"p": p_participante, "perm": p_permissao}
            )
        return True
    except Exception:
        await session.rollback()
        return False

# ============================================================
# FastAPI
# ============================================================

app = FastAPI(
    title="DB Control API",
    version="1.0.0",
)

app.middleware("http")(session_middleware)

@app.get("/health/")
async def root():
    return {
        "ok": True,
        "msg": "API online",
        "schema": DB_SCHEMA,
        "database": DB_NAME,
        "host": DB_HOST,
    }

@app.get("/middleware")
async def teste(request: Request):
    return {
        "participante": request.state.participante_id,
        "dispositivo": request.state.dispositivo_id
    }

@app.get("/modo/desenvolvimento")
async def modo_desenvolvimento(session: AsyncSession = Depends(get_session)):
    try:
        await session.execute(
            text("ALTER DATABASE :dbname SET plataforma.environment_mode = 'development'"),
            {"dbname": DB_NAME}
        )
        await session.commit()
        return {
            "status": "ok",
            "message": "Modo desenvolvimento ativado. Novas conexões usarão environment_mode = 'development'."
        }
    except Exception as e:
        await session.rollback()
        return {
            "status": "error",
            "message": str(e)
        }


# ============================================================
# /modo -> desenvolvimento <> produção
# ============================================================

@app.get("/modo/producao")
async def modo_producao(session: AsyncSession = Depends(get_session)):
    try:
        await session.execute(
            text("ALTER DATABASE :dbname SET plataforma.environment_mode = 'production'"),
            {"dbname": DB_NAME}
        )
        await session.commit()
        return {
            "status": "ok",
            "message": "Modo produção ativado. Novas conexões usarão environment_mode = 'production'."
        }
    except Exception as e:
        await session.rollback()
        return {
            "status": "error",
            "message": str(e)
        }


# ============================================================
# /send/code
# ============================================================

@app.get("/send/code/")
async def send_email_code(
    to: str,
    request: Request,
    session: AsyncSession = Depends(get_session),
):
    try:
        # Se tem @, é email completo; se não, é RA
        if "@" in to:
            destino = to.strip().lower()
        else:
            destino = f"{to}@mackenzista.com.br"

        # Validar dominio permitido
        dominio = destino.split("@")[1] if "@" in destino else ""
        if dominio not in emails_aceitos:
            return {
                "status": "error",
                "message": "Domínio de e-mail não permitido. Use @mackenzista.com.br ou @mackenzie.br."
            }

        codigo = gerar_codigo()
        smtp_host = os.getenv("SMTP_HOST", "smtp.gmail.com")
        smtp_port = int(os.getenv("SMTP_PORT", 587))

        smtp_user = os.getenv("SMTP_USER")
        smtp_password = os.getenv("SMTP_PASSWORD")

        if not smtp_user or not smtp_password:
            raise Exception("SMTP_USER ou SMTP_PASSWORD não configurados")

        html = f"""
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
</head>

<body style="
    margin:0;
    background:#0b0f14;
    font-family:Arial, Helvetica, sans-serif;
    color:#ffffff;
">

<div style="
    max-width:600px;
    margin:auto;
    padding:40px 20px;
">

    <div style="text-align:center;margin-bottom:30px;">
        <img src="https://plataforma-576668051133.us-central1.run.app/logo.png"
        style="height:70px;">
    </div>

    <div style="
        background:#121821;
        border-radius:10px;
        padding:30px;
        box-shadow:0 0 20px rgba(0,0,0,0.4);
    ">

        <h2 style="
            color:#30e080;
            margin-top:0;
        ">
        Código de acesso
        </h2>

        <p style="color:#c7d0d9;font-size:15px;">
        Olá, use o código abaixo para acessar a plataforma:
        </p>

        <div style="
            margin:30px 0;
            background:#0e141b;
            border:1px solid #1f2a36;
            border-radius:8px;
            padding:20px;
            text-align:center;
        ">

            <span style="
                font-size:36px;
                letter-spacing:8px;
                font-weight:bold;
                color:#30e080;
                user-select:all;
            ">
            {codigo}
            </span>

        </div>

        <p style="
            font-size:13px;
            color:#7f8c9a;
        ">
        Basta selecionar o código acima e copiar.
        </p>

    </div>

    <div style="
        text-align:center;
        margin-top:25px;
        font-size:12px;
        color:#6a7684;
    ">
        MackAI - Liga de Inteligência Artificial do Mackenzie
    </div>

</div>

</body>
</html>
"""
        msg = EmailMessage()
        msg["Subject"] = "Seu código de acesso"
        msg["From"] = smtp_user
        msg["To"] = destino

        msg.set_content("Seu código de acesso é: " + codigo)
        msg.add_alternative(html, subtype="html")

        smtp = smtplib.SMTP(smtp_host, smtp_port, timeout=30)

        smtp.ehlo()
        smtp.starttls()
        smtp.ehlo()

        smtp.login(smtp_user, smtp_password)

        smtp.send_message(msg)
        smtp.quit()

        email_str = destino

        # Salvar código no banco de dados
        sql_email = text("""
        WITH ins AS (
            INSERT INTO email (email)
            VALUES (:email)
            ON CONFLICT (email) DO NOTHING
            RETURNING id
        )
        SELECT id FROM ins
        UNION ALL
        SELECT id FROM email WHERE email = :email
        LIMIT 1
        """)

        email_id = (
            await session.execute(sql_email, {"email": email_str})
        ).scalar()

        sql_codigo = text("""
            INSERT INTO codigo_email (email, dispositivo, codigo)
            VALUES (:email_id, :dispositivo, :codigo)
        """)

        await session.execute(
            sql_codigo,
            {
                "email_id": email_id,
                "dispositivo": request.state.dispositivo_id,
                "codigo": codigo
            }
        )

        await session.commit()

        return {
            "status": "ok",
            "message": "email enviado"
        }

    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }

# ============================================================
# /realizar/login
# ============================================================

@app.post("/realizar/login/")
async def realizar_login(
    identificador: str = Form(...),
    senha: str = Form(...),
    request: Request = None,
    session: AsyncSession = Depends(get_session),
):
    try:
        participante_id = None
        senha_db = None

        # ---------------------------------------------------
        # 1 - identificar se é RA ou email
        # ---------------------------------------------------
        if "@" in identificador:
            # É email: buscar na tabela email -> participante
            email_lower = identificador.strip().lower()

            # Validar dominio permitido
            dominio = email_lower.split("@")[1] if "@" in email_lower else ""
            if dominio not in emails_aceitos:
                return {
                    "status": "error",
                    "message": "Credenciais inválidas"
                }

            row = (
                await session.execute(
                    text("""
                    SELECT p.id, p.senha
                    FROM participante p
                    JOIN email e ON e.participante = p.id
                    WHERE e.email = :email
                    LIMIT 1
                    """),
                    {"email": email_lower}
                )
            ).mappings().first()

            if row:
                participante_id = row["id"]
                senha_db = row["senha"]
        else:
            # É RA: validar 8 dígitos e buscar por RA
            if not re.fullmatch(r"[0-9]{8}", identificador):
                return {
                    "status": "error",
                    "message": "Credenciais inválidas"
                }

            row = (
                await session.execute(
                    text("""
                    SELECT id, senha
                    FROM participante
                    WHERE ra = :ra
                    LIMIT 1
                    """),
                    {"ra": identificador}
                )
            ).mappings().first()

            if row:
                participante_id = row["id"]
                senha_db = row["senha"]

        if not participante_id or not senha_db:
            return {
                "status": "error",
                "message": "Credenciais inválidas"
            }

        # ---------------------------------------------------
        # 2 - verificar senha
        # ---------------------------------------------------
        if not verificar_senha(senha, senha_db):
            return {
                "status": "error",
                "message": "Credenciais inválidas"
            }

        # ---------------------------------------------------
        # 3 - vincular sessão ao dispositivo
        # ---------------------------------------------------
        dispositivo = request.state.dispositivo_id

        await session.execute(
            text("""
            DELETE FROM sessao
            WHERE dispositivo = :dispositivo
            """),
            {"dispositivo": dispositivo}
        )

        await session.execute(
            text("""
            INSERT INTO sessao (participante, dispositivo)
            VALUES (:participante, :dispositivo)
            """),
            {
                "participante": participante_id,
                "dispositivo": dispositivo
            }
        )

        await session.commit()

        return {
            "status": "ok",
            "message": "Login realizado com sucesso",
            "participante_id": participante_id
        }

    except Exception as e:
        await session.rollback()
        return {
            "status": "error",
            "message": str(e)
        }


# ============================================================
# /realizar/cadastro
# ============================================================

@app.post("/realizar/cadastro/")
async def realizar_cadastro(
    ra: str = Form(...),
    codigo: str = Form(...),
    nome: str = Form(...),
    senha: str = Form(...),
    email: str = Form(None),
    request: Request = None,
    session: AsyncSession = Depends(get_session),
):
    try:
        # ---------------------------------------------------
        # 1 - validar RA
        # ---------------------------------------------------
        if not re.fullmatch(r"[0-9]{8}", ra):
            return {"status": "error", "message": "RA inválido. Deve conter 8 dígitos."}

        # ---------------------------------------------------
        # 2 - determinar email
        # ---------------------------------------------------
        if email:
            email_destino = email.strip().lower()
            # Validar dominio permitido
            dominio = email_destino.split("@")[1] if "@" in email_destino else ""
            if dominio not in emails_aceitos:
                return {
                    "status": "error",
                    "message": "Domínio de e-mail não permitido. Use @mackenzista.com.br ou @mackenzie.br."
                }
        else:
            email_destino = f"{ra}@mackenzista.com.br"

        dispositivo = request.state.dispositivo_id

        # ---------------------------------------------------
        # 3 - verificar código válido
        # ---------------------------------------------------
        sql_codigo = text("""
        SELECT ce.id
        FROM codigo_email ce
        JOIN email e ON e.id = ce.email
        WHERE e.email = :email
        AND ce.codigo = :codigo
        AND ce.dispositivo = :dispositivo
        AND ce.validado IS NULL
        AND ce.criado > NOW() - interval '20 minutes'
        LIMIT 1
        """)

        row = (
            await session.execute(
                sql_codigo,
                {
                    "email": email_destino,
                    "codigo": codigo,
                    "dispositivo": dispositivo
                }
            )
        ).first()

        if not row:
            return {
                "status": "error",
                "message": "Código inválido ou expirado."
            }

        codigo_id = row[0]

        # ---------------------------------------------------
        # 4 - hash da senha
        # ---------------------------------------------------
        senha_hash = hash_senha(senha)

        # ---------------------------------------------------
        # 5 - inserir participante
        # ---------------------------------------------------
        sql_participante = text("""
        INSERT INTO participante (ra, nome, senha)
        VALUES (:ra, :nome, :senha)
        RETURNING id
        """)

        participante_id = (
            await session.execute(
                sql_participante,
                {
                    "ra": ra,
                    "nome": nome,
                    "senha": senha_hash
                }
            )
        ).scalar()

        # ---------------------------------------------------
        # 6 - vincular email ao participante
        # ---------------------------------------------------
        sql_vincular_email = text("""
        UPDATE email
        SET participante = :participante
        WHERE email = :email
        """)

        await session.execute(
            sql_vincular_email,
            {
                "participante": participante_id,
                "email": email_destino
            }
        )

        # ---------------------------------------------------
        # 7 - marcar código como validado
        # ---------------------------------------------------
        sql_validar = text("""
        UPDATE codigo_email
        SET validado = NOW()
        WHERE id = :id
        """)

        await session.execute(sql_validar, {"id": codigo_id})

        sql_sessao = text("""
        INSERT INTO sessao (participante, dispositivo)
        VALUES (:participante, :dispositivo)
        """)

        await session.execute(
            sql_sessao, 
            {
                "participante": participante_id, 
                "dispositivo": dispositivo
            }
        )

        await session.commit()

        return {
            "status": "ok",
            "message": "Cadastro realizado com sucesso."
        }

    except Exception as e:
        await session.rollback()
        return {
            "status": "error",
            "message": str(e)
        }


# ============================================================
# /realizar/recuperar-senha
# ============================================================

@app.post("/realizar/recuperar-senha/")
async def recuperar_senha(
    identificador: str = Form(...),
    codigo: str = Form(...),
    senha: str = Form(...),
    request: Request = None,
    session: AsyncSession = Depends(get_session),
):
    try:
        dispositivo = request.state.dispositivo_id

        # ---------------------------------------------------
        # 1 - determinar email e RA
        # ---------------------------------------------------
        if "@" in identificador:
            email_destino = identificador.strip().lower()

            # Validar dominio permitido
            dominio = email_destino.split("@")[1] if "@" in email_destino else ""
            if dominio not in emails_aceitos:
                return {
                    "status": "error",
                    "message": "Domínio de e-mail não permitido."
                }

            # Buscar RA do participante vinculado a este email
            row = (
                await session.execute(
                    text("""
                    SELECT p.ra
                    FROM participante p
                    JOIN email e ON e.participante = p.id
                    WHERE e.email = :email
                    LIMIT 1
                    """),
                    {"email": email_destino}
                )
            ).mappings().first()

            if not row:
                return {
                    "status": "error",
                    "message": "Código inválido ou expirado."
                }

            ra = row["ra"]
        else:
            ra = identificador
            if not re.fullmatch(r"[0-9]{8}", ra):
                return {
                    "status": "error",
                    "message": "Código inválido ou expirado."
                }
            email_destino = f"{ra}@mackenzista.com.br"

        # ---------------------------------------------------
        # 2 - validar código
        # ---------------------------------------------------
        row = (
            await session.execute(
                text("""
                SELECT ce.id
                FROM codigo_email ce
                JOIN email e ON e.id = ce.email
                WHERE e.email = :email
                AND ce.codigo = :codigo
                AND ce.dispositivo = :dispositivo
                AND ce.validado IS NULL
                AND ce.criado > NOW() - interval '20 minutes'
                LIMIT 1
                """),
                {
                    "email": email_destino,
                    "codigo": codigo,
                    "dispositivo": dispositivo
                }
            )
        ).first()

        if not row:
            return {
                "status": "error",
                "message": "Código inválido ou expirado."
            }

        codigo_id = row[0]

        # ---------------------------------------------------
        # 3 - atualizar senha
        # ---------------------------------------------------
        senha_hash = hash_senha(senha)

        await session.execute(
            text("""
            UPDATE participante
            SET senha = :senha
            WHERE ra = :ra
            """),
            {"senha": senha_hash, "ra": ra}
        )

        # marcar código como usado
        await session.execute(
            text("""
            UPDATE codigo_email
            SET validado = NOW()
            WHERE id = :id
            """),
            {"id": codigo_id}
        )

        await session.commit()

        return {
            "status": "ok",
            "message": "Senha atualizada com sucesso."
        }

    except Exception as e:
        await session.rollback()
        return {
            "status": "error",
            "message": str(e)
        }


# ============================================================
# /realizar/logout
# ============================================================

@app.get("/realizar/logout/")
async def realizar_logout(
    request: Request,
    session: AsyncSession = Depends(get_session),
):
    try:
        dispositivo_id = getattr(request.state, "dispositivo_id", None)

        if dispositivo_id:
            await session.execute(
                text("""
                DELETE FROM sessao
                WHERE dispositivo = :dispositivo
                """),
                {"dispositivo": dispositivo_id}
            )
            await session.commit()

        response = RedirectResponse("/login", status_code=302)

        return response

    except Exception as e:
        await session.rollback()
        return {"error": str(e)}
        

# ============================================================
# /db/procedure
# ============================================================

@app.get("/db/procedure/")
async def listar_procedures(session: AsyncSession = Depends(get_session)):
    try:
        sql = text("""
            SELECT
                p.proname AS name,
                pg_get_function_arguments(p.oid) AS args,
                obj_description(p.oid, 'pg_proc') AS comment
            FROM pg_proc p
            JOIN pg_namespace n ON n.oid = p.pronamespace
            WHERE n.nspname = :schema
              AND p.prokind = 'p'   -- 'p' = PROCEDURE
            ORDER BY name;
        """)

        rows = await session.execute(sql, {"schema": DB_SCHEMA})

        procedures = []
        for r in rows.mappings().all():
            procedures.append({
                "name": r["name"],
                "arguments": r["args"],
                "comment": r["comment"],
            })

        return success({"procedures": procedures})
    except Exception as e:
        return failure(str(e))


@app.get("/db/procedure/{nome}")
async def executar_procedure(
    nome: str,
    request: Request,
    session: AsyncSession = Depends(get_session),
):
    """
    Executa uma procedure lendo os parâmetros automaticamente.
    Os GET params devem vir sem 'in_'.
    """
    try:
        nome = validate_identifier(nome)

        # Captura parâmetros enviados na URL
        query_params = dict(request.query_params)

        # 1 - Buscar parâmetros da procedure no PostgreSQL
        sql = text("""
            SELECT
                p.proname AS name,
                unnest(string_to_array(pg_get_function_arguments(p.oid), ',')) AS arg
            FROM pg_proc p
            JOIN pg_namespace n ON n.oid = p.pronamespace
            WHERE n.nspname = :schema
              AND p.prokind = 'p'
              AND p.proname = :nome;
        """)

        rows = (await session.execute(
            sql, {"schema": DB_SCHEMA, "nome": nome})
        ).mappings().all()

        if not rows:
            return failure(f"Procedure '{nome}' não encontrada.")

        # 2 - Interpretar parâmetros
        parametros_pg = []
        for r in rows:
            raw = r["arg"].strip()
            parts = raw.split()
            modo = parts[0].upper()
            pg_name = parts[1]
            
            # Detectar se tem DEFAULT (a palavra "DEFAULT" aparece depois do tipo)
            has_default = "DEFAULT" in parts
            
            # Reconstruir o tipo corretamente (pode ser composto como "character varying")
            # O tipo vai de parts[2] até encontrar "DEFAULT" ou até o final
            tipo_parts = []
            for p in parts[2:]:
                if p == "DEFAULT":
                    break
                tipo_parts.append(p)
            tipo = " ".join(tipo_parts)
            
            clean_name = pg_name
            if clean_name.startswith("in_"):
                clean_name = clean_name[3:]
        
            parametros_pg.append({
                "mode": modo,
                "pg_name": pg_name,
                "clean_name": clean_name,
                "type": tipo,
                "has_default": has_default  # NOVO
            })

        # 3 - Verificar obrigatórios
        obrigatorios = [
            p for p in parametros_pg
            if p["mode"] == "IN" 
            and p["pg_name"] != "in_executado_por"
            and not p["has_default"]  # ← IGNORAR parâmetros com DEFAULT
        ]

        faltando = [
            p["clean_name"] for p in obrigatorios
            if p["clean_name"] not in query_params
        ]

        if faltando:
            return failure({
                "erro": "Parâmetros obrigatórios faltando",
                "faltando": faltando,
                "recebidos": list(query_params.keys()),
                "esperados": [p["clean_name"] for p in obrigatorios]
            })

        # 4 - Casting automático
        args_valores = []
        participante_id = request.state.participante_id

        for p in parametros_pg:

            pg_name = p["pg_name"]
            key = p["clean_name"]
            tipo = p["type"].lower()

            # 🔒 Parâmetro protegido
            if pg_name == "in_executado_por":
                valor = participante_id   # None vira NULL automaticamente
                args_valores.append(valor)
                continue

            # valor vindo da URL
            if key in query_params:
                valor = query_params[key]
            else:
                valor = None

            if valor is not None:

                if tipo in ("integer", "int4", "int"):
                    valor = int(valor)

                elif tipo in ("bigint", "int8"):
                    valor = int(valor)

                elif tipo in ("decimal", "numeric"):
                    valor = float(str(valor).replace(",", "."))

                elif tipo in ("boolean", "bool"):          # ← NOVO
                    if isinstance(valor, str):
                        valor = valor.lower() in ("true", "1", "yes", "on")
                    else:
                        valor = bool(valor)

                elif tipo in (
                    "timestamp",
                    "timestamptz",
                    "timestamp with time zone",
                    "timestamp without time zone",
                ):
                    valor = datetime.fromisoformat(valor)

                elif tipo == "date":
                    valor = date.fromisoformat(valor)

                elif tipo.startswith("time"):
                    valor = time.fromisoformat(valor)

                else:
                    valor = str(valor)

            args_valores.append(valor)

        # 5 - Criar SQL CALL dinâmico
        placeholders = ",".join([f":arg{i}" for i in range(len(args_valores))])
        exec_sql = text(
            f'CALL "{DB_SCHEMA}".{nome}({placeholders});'
        )

        param_map = {f"arg{i}": v for i, v in enumerate(args_valores)}

        # 6 - Executar procedure
        await session.execute(exec_sql, param_map)
        await session.commit()

        return success({
            "executado": nome,
            "parametros_usados": param_map
        })

    except Exception as e:
        await session.rollback()
        return failure(str(e))


# ============================================================
# /db/function
# ============================================================

@app.get("/db/function/")
async def listar_funcoes(session: AsyncSession = Depends(get_session)):
    try:
        sql = text("""
            SELECT
                p.proname AS name,
                pg_get_function_arguments(p.oid) AS args,
                pg_get_function_result(p.oid) AS returns,
                obj_description(p.oid, 'pg_proc') AS comment
            FROM pg_proc p
            JOIN pg_namespace n ON n.oid = p.pronamespace
            WHERE n.nspname = :schema
              AND p.prokind = 'f'     -- 'f' = function
            ORDER BY name;
        """)

        rows = await session.execute(sql, {"schema": DB_SCHEMA})

        functions = []
        for r in rows.mappings().all():
            functions.append({
                "name": r["name"],
                "arguments": r["args"],
                "returns": r["returns"],
                "comment": r["comment"],
            })

        return success({"functions": functions})

    except Exception as e:
        return failure(str(e))


@app.get("/db/function/{nome}")
async def executar_funcao(nome: str, session: AsyncSession = Depends(get_session)):
    try:
        nome = validate_identifier(nome)

        exists_sql = text("""
            SELECT COUNT(*)
            FROM information_schema.routines
            WHERE routine_schema = :schema
              AND routine_type = 'FUNCTION'
              AND routine_name = :nome;
        """)
        exists = (await session.execute(exists_sql, {"schema": DB_SCHEMA, "nome": nome})).scalar()

        if not exists:
            return failure(f"Função '{nome}' não encontrada no schema '{DB_SCHEMA}'.")

        exec_sql = text(f'SELECT "{DB_SCHEMA}".{nome}();')
        result = await session.execute(exec_sql)
        return success(result.scalar())

    except Exception as e:
        return failure(str(e))


# ============================================================
# /db/table
# ============================================================

@app.get("/db/table/")
async def listar_tabelas(session: AsyncSession = Depends(get_session)):
    try:
        sql = text("""
            SELECT
                c.relname AS table_name,
                obj_description(c.oid) AS comment
            FROM pg_class c
            JOIN pg_namespace n ON n.oid = c.relnamespace
            WHERE n.nspname = :schema
              AND c.relkind = 'r'      -- tabelas normais
            ORDER BY table_name;
        """)

        rows = await session.execute(sql, {"schema": DB_SCHEMA})

        tables = []
        for r in rows.mappings().all():
            tables.append({
                "table": r["table_name"],
                "comment": r["comment"],
            })

        return success({"tables": tables})
    except Exception as e:
        return failure(str(e))


@app.get("/db/table/{nome}")
async def listar_tabela(
    nome: str,
    limit: Optional[int] = None,
    session: AsyncSession = Depends(get_session),
):
    try:
        nome = validate_identifier(nome)

        exists_sql = text("""
            SELECT COUNT(*)
            FROM information_schema.tables
            WHERE table_schema = :schema
              AND table_name   = :nome;
        """)
        exists = (await session.execute(exists_sql, {"schema": DB_SCHEMA, "nome": nome})).scalar()

        if not exists:
            return failure(f"Tabela '{nome}' não existe no schema '{DB_SCHEMA}'.")

        # Definir coluna de ordenação
        col_sql = text("""
            SELECT column_name
            FROM information_schema.columns
            WHERE table_schema = :schema
              AND table_name   = :nome
              AND column_name IN ('atualizado', 'tempo')
            ORDER BY CASE column_name
                WHEN 'atualizado' THEN 1
                WHEN 'tempo'      THEN 2
            END
            LIMIT 1;
        """)
        col = (await session.execute(col_sql, {"schema": DB_SCHEMA, "nome": nome})).scalar()

        order_clause = f'ORDER BY "{col}" DESC' if col else ""
        limit_clause = "LIMIT :limit" if limit is not None else ""

        sql = text(f'SELECT * FROM "{DB_SCHEMA}".{nome} {order_clause} {limit_clause};')
        params = {}
        if limit is not None:
            params["limit"] = limit

        rows = await session.execute(sql, params)
        return success([dict(r) for r in rows.mappings().all()])

    except Exception as e:
        return failure(str(e))

@app.get("/db/reset")
async def reset_db(
    vazio: bool = False,
):
    """
    Reseta o banco executando todos os .sql do repositório.
    - vazio = false -> executa TODOS, inclusive ZZZ*.sql
    - vazio = true  -> ignora ARQUIVOS que começam com 'ZZZ'
    """

    GITHUB_SQL_DIR_URL = (
        "https://api.github.com/repos/ligamackai/plataforma/contents/SQL"
    )

    try:
        # 1. Buscar lista de arquivos no GitHub
        with urlopen(GITHUB_SQL_DIR_URL) as resp:
            files = json.load(resp)

        # 2. Filtrar somente .sql e montar URL RAW com quote()
        sql_files = []
        for f in files:
            name = f["name"]
            if not name.endswith(".sql"):
                continue

            raw_url = (
                "https://raw.githubusercontent.com/"
                "rafavidal1709/mack-ai-plataforma/main/postgreSQL/"
                + quote(name)
            )

            sql_files.append({"name": name, "download_url": raw_url})

        # 3. Ordenar alfabeticamente
        sql_files.sort(key=lambda x: x["name"])

        executados = []
        ignorados = []

        # Executor de thread
        executor = ThreadPoolExecutor(max_workers=1)

        # Função que executa SQL bruto via psycopg2
        def executar_sql_bruto(sql_text: str, filename: str):
            try:
                conn = psycopg2.connect(
                    dbname=DB_NAME,
                    user=DB_USER,
                    password=DB_PASSWORD,
                    host=DB_HOST,
                    port=DB_PORT,
                )
                conn.autocommit = True
                cur = conn.cursor()
                cur.execute(sql_text)
                cur.close()
                conn.close()
            except Exception as e:
                raise Exception(f"Erro ao executar '{filename}': {e}")

        # 4. Loop pelos arquivos SQL
        for meta in sql_files:
            name = meta["name"]

            # Ignorar arquivos ZZZ somente se vazio=True
            if vazio and name.startswith("ZZZ"):
                ignorados.append(name)
                continue

            # Baixar SQL bruto
            with urlopen(meta["download_url"]) as file_resp:
                sql_content = file_resp.read().decode("utf-8")

            # Executar em thread separada
            loop = asyncio.get_running_loop()
            await loop.run_in_executor(executor, executar_sql_bruto, sql_content, name)

            executados.append(name)

        # Sucesso
        return success({
            "msg": "Reset do banco concluído com sucesso.",
            "vazio": vazio,
            "executados": executados,
            "ignorados": ignorados,
        })

    except Exception as e:
        return failure(f"Erro ao resetar banco: {e}")

init_router(SessionLocal, engine)

@app.api_route("/{full_path:path}", methods=["GET", "POST"])
async def catch_all(full_path: str, request: Request):

    interceptar = ['encontro', 'tarefa', 'grupo', 'participante', 'equipe']

    for i in interceptar:

        if full_path.startswith(i + "/"):

            restante = full_path[len(i) + 1:]
            partes = [p for p in restante.split("/") if p]

            if not partes:
                break

            try:
                id_int = int(partes[0])
            except ValueError:
                break

            # --------------------------------------------------
            # CASO ESPECIAL:
            # /grupo/{id}/tarefa
            # /grupo/{id}/encontro
            # /grupo/{id}/tarefa/...
            # /grupo/{id}/encontro/...
            # Vai para root: tarefa.py ou encontro.py
            # com parâmetro grupo={id}
            # E, se houver mais caminho, trata como subrota normal
            # --------------------------------------------------
            if i == "grupo" and len(partes) >= 2 and partes[1] in ["tarefa", "encontro"]:
                novo_root = partes[1]
                resto = partes[2:]

                if resto:
                    novo_full_path = novo_root + "/" + "/".join(resto)
                else:
                    novo_full_path = novo_root

                return await dynamic_router(
                    novo_full_path,
                    request,
                    {"grupo": id_int}
                )

            # --------------------------------------------------
            # COMPORTAMENTO PADRÃO:
            # /tarefa/29           -> tarefa/item      com id=29
            # /tarefa/29/editar    -> tarefa/editar    com id=29
            # /tarefa/29/x/y       -> tarefa/x/y       com id=29
            # --------------------------------------------------
            if len(partes) == 1:
                destino = i + "/item"
            else:
                destino = i + "/" + "/".join(partes[1:])

            return await dynamic_router(
                destino,
                request,
                {"id": id_int}
            )

    return await dynamic_router(full_path, request)
