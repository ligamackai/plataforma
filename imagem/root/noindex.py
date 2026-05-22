def render(request, context):
    return {
        "title": "Página não encontrada",
        "body": "<h1>404 - Página não encontrada</h1>",
        "style": "h1 { color: red; }"
    }
