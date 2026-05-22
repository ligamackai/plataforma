import importlib.util
import sys
import os
import re
import asyncio
from pathlib import Path
from typing import Optional, Any, Dict
import mimetypes
from fastapi import Request
from fastapi.responses import Response, StreamingResponse, RedirectResponse
from datetime import timedelta
from google.cloud import storage
from google.auth import default
from google.auth import iam
from google.auth.transport.requests import Request as GoogleRequest
from google.cloud.storage import Blob

ROOT_DIR = Path("root")
BUCKET_NAME = os.getenv("BUCKET")

credentials, project = default()

signer = iam.Signer(
    GoogleRequest(),
    credentials,
    credentials.service_account_email
)

storage_client = storage.Client(credentials=credentials)

SessionLocal = None
engine = None

def init_router(db_session, db_engine):
    global SessionLocal, engine
    SessionLocal = db_session
    engine = db_engine

def sanitize_path(path: str) -> str:

    # remove query string
    path = path.split("?", 1)[0]

    path = path.strip().strip("/")

    if not path:
        return ""

    if not re.match(r"^[a-zA-Z0-9/_\-.]+$", path):
        raise ValueError("Invalid path")

    if "//" in path:
        raise ValueError("Invalid path")

    return path

def generate_signed_url(blob):
    request = GoogleRequest()

    url = blob.generate_signed_url(
        version="v4",
        expiration=timedelta(minutes=15),
        method="GET",
        credentials=credentials,
        service_account_email=credentials.service_account_email,
        access_token=credentials.token,
    )

    return url

def load_local_module(path: str):
    file_path = ROOT_DIR / f"{path}.py"
    if not file_path.exists():
        return None

    module_name = f"local_{path.replace('/', '_')}"
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Falha ao carregar módulo local: {path}")

    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


def load_bucket_module(path: str):
    bucket = storage_client.bucket(BUCKET_NAME)
    blob = bucket.blob(path)
    if not blob.exists():
        return None

    import tempfile
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".py")
    blob.download_to_filename(tmp.name)

    module_name = f"bucket_{path.replace('/', '_')}"

    try:
        spec = importlib.util.spec_from_file_location(module_name, tmp.name)
        if spec is None or spec.loader is None:
            raise RuntimeError(f"Falha ao carregar módulo bucket: {path}")

        module = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = module
        spec.loader.exec_module(module)
        return module
    finally:
        os.unlink(tmp.name)


async def execute_module(module, request_data: Dict[str, Any], request):
    if SessionLocal is None:
        raise RuntimeError("Router não inicializado: chame init_router(...) no main.py")

    async with SessionLocal() as db:
        context = {
            "db": db,
            "engine": engine,
            "request": request
        }

        result = module.render(request_data, context)

        if asyncio.iscoroutine(result):
            result = await result

        if isinstance(result, str):
            result = {"body": result}
        # ===============================
        # REDIRECT
        # ===============================
        if "redirect" in result:
            return RedirectResponse(result["redirect"], status_code=302)

        # ===============================
        # DADOS DA PÁGINA
        # ===============================
        body = result.get("body", "")
        title = result.get("title", "Plataforma")
        description = result.get("description", "")
        extra_style = result.get("style", "")

        # ===============================
        # MENU (root/menu.py)
        # ===============================
        menu_html = ""
        menu_style = ""

        try:
            menu_module = load_local_module("menu")
            if menu_module and callable(getattr(menu_module, "render", None)):
                menu_result = menu_module.render(request_data, context)

                if asyncio.iscoroutine(menu_result):
                    menu_result = await menu_result

                if isinstance(menu_result, dict):
                    menu_html = menu_result.get("body", "")
                    menu_style = menu_result.get("style", "")
                else:
                    menu_html = str(menu_result)
        except Exception as e:
            menu_html = f"<div>Erro menu: {e}</div>"

        # ===============================
        # CSS BASE (root/style.css)
        # ===============================
        css = ""
        css_path = ROOT_DIR / "style.css"
        if css_path.exists():
            with open(css_path, "r", encoding="utf-8") as f:
                css = f.read()

        # ===============================
        # HTML FINAL
        # ===============================
        html = f"""
<!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="UTF-8">
    <title>{title}</title>
    <meta name="description" content="{description}">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link rel="icon" href="/icon.png" type="image/png">
    <style>
    {css}
    {extra_style}
    {menu_style}
    </style>
</head>
<body>

    <div class="sidebar">
        {menu_html}
    </div>

    <div class="main">
        {body}
    </div>

</body>
</html>
        """

        return Response(
            content=html,
            status_code=result.get("status", 200),
            media_type="text/html",
        )

def stream_bucket_file(blob):
    def file_iterator():
        with blob.open("rb") as f:
            yield from f

    return StreamingResponse(
        file_iterator(),
        media_type=blob.content_type
    )


async def dynamic_router(full_path: str, request: Request, query: dict = None):
    full_path = sanitize_path(full_path)

    if full_path == "":
        full_path = "index"

    body = await request.body()

    request_data = {
        "method": request.method,
        "path": request.url.path,
        "query": dict(request.query_params),
        "headers": dict(request.headers),
        "body": body.decode("utf-8"),
    }

    if isinstance(query, dict):
        for k in query.keys():
            request_data['query'][k] = query[k]

    # =========================================
    # 1) BUCKET PY (PRIORIDADE MÁXIMA)
    # =========================================
    module = load_bucket_module(f"{full_path}.py")
    if module and callable(getattr(module, "render", None)):
        return await execute_module(module, request_data, request)

    # =========================================
    # 2) BUCKET INDEX
    # =========================================
    module = load_bucket_module(f"{full_path}/index.py")
    if module and callable(getattr(module, "render", None)):
        return await execute_module(module, request_data, request)

    # =========================================
    # 3) LOCAL PY (root/)
    # =========================================
    module = load_local_module(full_path)
    if module and callable(getattr(module, "render", None)):
        return await execute_module(module, request_data, request)

    # =========================================
    # 4) LOCAL INDEX
    # =========================================
    module = load_local_module(f"{full_path}/index")
    if module and callable(getattr(module, "render", None)):
        return await execute_module(module, request_data, request)

    # =========================================
    # 5) STATIC LOCAL (root/)
    # =========================================
    local_file = ROOT_DIR / full_path

    if local_file.exists() and local_file.is_file():
        def file_iterator():
            with open(local_file, "rb") as f:
                yield from f

        media_type, _ = mimetypes.guess_type(full_path)

        if not media_type:
            media_type = "application/octet-stream"

        return StreamingResponse(file_iterator(), media_type=media_type)

    # =========================================
    # STATIC BUCKET (REDIRECT DIRETO - CORRETO)
    # =========================================
    bucket = storage_client.bucket(BUCKET_NAME)
    blob = bucket.blob(full_path)

    if blob.exists():

        # garante token válido
        credentials.refresh(GoogleRequest())

        url = blob.generate_signed_url(
            version="v4",
            expiration=timedelta(minutes=15),
            method="GET",
            service_account_email=credentials.service_account_email,
            access_token=credentials.token,
        )

        return RedirectResponse(url)

    # =========================================
    # 7) 404 (via noindex.py se existir)
    # =========================================
    module = load_local_module("noindex")

    if module and callable(getattr(module, "render", None)):
        return await execute_module(module, request_data, request)

    return Response("Not Found", status_code=404)
