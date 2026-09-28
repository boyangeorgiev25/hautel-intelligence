# Engine API for Fly.io (region fra). Runs engine/api.py; secrets come from `fly secrets`.
FROM python:3.12-slim
WORKDIR /app
RUN pip install --no-cache-dir uv
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev --no-install-project
COPY engine ./engine
COPY tests ./tests
RUN uv sync --frozen --no-dev
ENV PATH="/app/.venv/bin:$PATH" HAUTEL_API_HOST=0.0.0.0 HAUTEL_API_PORT=8080
EXPOSE 8080
CMD ["hautel-api"]
