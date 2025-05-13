FROM python:3.11-slim

WORKDIR /apps

# Устанавливаем системные зависимости
RUN apt-get update && apt-get install -y \
    gcc \
    libjpeg-dev \
    zlib1g-dev \
    && rm -rf /var/lib/apt/lists/*

COPY . .
RUN pip install --no-cache-dir -r requirements.txt

CMD python Parse.py