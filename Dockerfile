FROM python:3.12-slim-bookworm

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

COPY app /app/
COPY pyproject.toml /pyproject.toml
COPY uv.lock /uv.lock
COPY .python-version /python-version

EXPOSE 8000

ENTRYPOINT [ "uv", "run", "fastapi", "dev" ]