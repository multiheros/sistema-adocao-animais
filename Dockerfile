# Simple dev/demo Dockerfile for the Django app
# Usage:
#   docker build -t sistema-adocao:dev .
#   docker run --rm -it -p 8000:8000 -v $(pwd):/app sistema-adocao:dev

FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

# System deps
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libjpeg-dev \
    zlib1g-dev \
    git \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install deps first for better caching
COPY requirements.txt /app/requirements.txt
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy project
COPY . /app

# Collect static is not required for dev; using runserver
# Expose port
EXPOSE 8000

# Default envs for dev
ENV DJANGO_DEBUG=1 \
    DJANGO_ALLOWED_HOSTS=* \
    PY=python

# Entrypoint: run development server binding all interfaces
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
