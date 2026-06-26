FROM python:3.12-slim-bookworm
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app
COPY pyproject.toml uv.lock ./
RUN uv sync --no-dev --no-install-project --frozen
COPY . .

ENV PATH="/app/.venv/bin:$PATH"
CMD ["celery", "-A", "worker", "worker", "--loglevel=info"]
