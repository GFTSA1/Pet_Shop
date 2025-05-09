FROM python:3.12

WORKDIR /app

COPY requirements.txt requirements.txt

RUN apt-get update && apt-get install -y \
    python3-dev \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*


RUN pip install --no-cache-dir -r requirements.txt



COPY . .


ENV DATABASE_NAME=pets_shop
ENV DATABASE_USER=postgres
ENV DATABASE_PASSWORD=1939
ENV DATABASE_HOST=db
ENV DATABASE_PORT=5432

CMD ["gunicorn", "Pet_Shop.wsgi:application", "--bind", "0.0.0.0:8000"]
