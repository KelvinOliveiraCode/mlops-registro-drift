FROM python:3.12-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

COPY pyproject.toml README.md ./
RUN pip install --no-cache-dir -e ".[dev]"

COPY src ./src
COPY tests ./tests

CMD ["python", "-m", "mlops_registro_drift"]
