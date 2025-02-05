# Dockerfile
FROM python:3.11

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV DATABASE_NAME=pets_shop
ENV DATABASE_USER=postgres
ENV DATABASE_PASSWORD=1939
ENV DATABASE_HOST=db
ENV DATABASE_PORT=5432

CMD ["gunicorn", "project.wsgi:application", "--bind", "0.0.0.0:8000"]