FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Folder for SQLite DB when not using external DB
RUN mkdir -p /data
ENV DATABASE_URL=sqlite:////data/cobblepaste.db

ENV FLASK_APP=app.py

CMD ["gunicorn", "-b", "0.0.0.0:8000", "app:app"]
