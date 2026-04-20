FROM astral/uv:python3.13-bookworm-slim

WORKDIR /app

COPY uv.lock pyproject.toml ./
RUN uv sync --frozen --no-dev --no-install-workspace

COPY . .

RUN uv sync --frozen --no-dev --offline

ENV PYTHONPATH=.

CMD ["bash", "start.sh"]
