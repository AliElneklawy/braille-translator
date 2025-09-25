FROM ghcr.io/astral-sh/uv:0.8.22-debian

WORKDIR /app

COPY pyproject.toml .

RUN uv venv \
    && uv pip install .

COPY . .

EXPOSE 8000

CMD ["uvicorn", "src.webapp.app:app", "--host", "0.0.0.0", "--port", "8000"]
