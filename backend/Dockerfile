FROM astral/uv:python3.13-bookworm-slim

WORKDIR /app

RUN groupadd --system appgroup && \
    useradd --system --no-create-home --gid appgroup appuser

COPY uv.lock pyproject.toml ./
RUN uv sync --frozen --no-dev --no-install-workspace

COPY . .

RUN uv sync --frozen --no-dev --offline

RUN chown -R appuser:appgroup /app

RUN mkdir -p /home/appuser/.cache/uv && \
    chown -R appuser:appgroup /home/appuser

ENV PYTHONPATH=.

USER appuser

CMD ["bash", "start.sh"]