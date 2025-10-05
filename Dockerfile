FROM python:3.10.13-slim

RUN apt-get update && apt-get install --no-install-recommends -y curl ca-certificates\
    build-essential && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

ADD https://astral.sh/uv/install.sh /uv-installer.sh

RUN sh /uv-installer.sh && rm /uv-installer.sh

ENV PATH="/root/.local/bin:${PATH}"

WORKDIR /app

COPY pyproject.toml .

RUN uv sync

ENV PATH="/app/.venv/bin:${PATH}"

COPY . .

EXPOSE 8000

CMD ["uvicorn", "src.webapp.app:app", "--host", "0.0.0.0", "--port", "8000"]
