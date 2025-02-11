FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt requirements.txt
RUN apt-get update && apt-get install -y build-essential libpq-dev

COPY . .

RUN pip install --no-cache-dir -r requirements.txt

ENV DATABASE_NAME=pets_shop
ENV DATABASE_USER=postgres
ENV DATABASE_PASSWORD=1939
ENV DATABASE_HOST=db
ENV DATABASE_PORT=5432

# Запуск gunicorn
CMD ["/usr/local/bin/gunicorn", "Pet_Shop.wsgi:application", "--bind", "0.0.0.0:8000"]