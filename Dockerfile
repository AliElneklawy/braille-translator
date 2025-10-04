# FROM ghcr.io/astral-sh/uv:0.8.22-debian

# WORKDIR /app

# COPY pyproject.toml .

# RUN uv venv \
#     && uv pip install .

# COPY . .

# EXPOSE 8000

# CMD ["uvicorn", "src.webapp.app:app", "--host", "0.0.0.0", "--port", "8000"]


FROM python:3.10.13-alpine

RUN apt-get update && apt-get install --no-install-recommends -y \
    build-essential && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

ADD https://astral.sh/uv/install.sh /install.sh

RUN chmod -R 755 /install.sh && /install.sh && rm /install.sh

ENV PATH="/root/.local/bin:${PATH}"

WORKDIR /app

COPY pyproject.toml .

RUN uv sync

ENV PATH="/app/.venv/bin:${PATH}"

COPY . .

EXPOSE 8000

CMD ["uvicorn", "src.webapp.app:app", "--port", "8000"]
