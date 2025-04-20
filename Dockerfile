FROM python:3.13-slim

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /backend

COPY pyproject.toml uv.lock .python-version ./

RUN uv sync --no-cache-dir --no-dev

COPY app ./app

EXPOSE 8001

CMD ["uv", "run", "fastapi", "dev", "--host", "0.0.0.0", "--port", "8001"]