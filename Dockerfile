# Используем официальный образ с uv
FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim

WORKDIR /app

# Настройки для оптимизации Python в контейнере
ENV UV_COMPILE_BYTECODE=0
ENV UV_LINK_MODE=copy
ENV PYTHONUNBUFFERED=1

# 1. Сначала зависимости (слой кэшируется)
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-install-project --no-dev

# 2. Теперь код
COPY . .

# 3. Скачиваем ассеты (шахматные фигуры) внутрь образа
# Чтобы фронтенд работал автономно
RUN uv run scripts/download_assets.py

EXPOSE 8000

# Запуск
CMD ["uv", "run", "uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]