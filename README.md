[Entrar na Plataforma MACK AI](https://plataforma-576668051133.us-central1.run.app/)

# Estrutura

- Imagem: PostgreeSQL 15

Banco de dados conectado pelo SQL Alchemy.

Pasta: [SQL](https://github.com/ligamackai/plataforma/tree/main/SQL)


- Imagem: python:3.12-slim

Recebe as requisições e distribui em endpoints dinâmicos, o que permite o desenvolvimento modular e paralelo da plataforma.

Arquivo: [imagem.tar.gz](https://github.com/ligamackai/plataforma/tree/main/imagem.tar.gz)


- Bucket

Guarda módulos/arquivos para compor páginas específicas e permite atualização em tempo real e concorrente de diferentes endpoints.
