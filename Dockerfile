FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

COPY requirements.txt /app/requirements.txt
RUN if [ -f /app/requirements.txt ]; then \
        pip install -r /app/requirements.txt; \
    else \
        pip install "Django>=5.0,<6.0" "gunicorn>=21.0,<22.0" "psycopg[binary]>=3.1,<4.0"; \
    fi

COPY . /app

EXPOSE 8000

CMD ["gunicorn", "core.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "3", "--threads", "2", "--timeout", "60"]
