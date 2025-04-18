FROM python:3.13-slim

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /backend
COPY pyproject.toml /backend/pyproject.toml
COPY uv.lock /backend/uv.lock
COPY .python-version /backend/python-version

RUN uv sync --no-cache-dir --no-dev

COPY app /backend/app

CMD [ "uv", "run", "fastapi", "dev", "--port", "8001" ]