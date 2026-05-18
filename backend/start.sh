uv run --no-dev taskiq worker src.infra.taskiq:broker &
uv run --no-dev fastapi run src/main.py
