FROM python:3.10-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY src ./src
COPY data ./data

ENV MEGAGYM_CSV_PATH=./data/megaGymDataset.csv \
    DB_PATH=./data/gymcoach.db \
    PORT=8080

EXPOSE 8080

CMD ["gunicorn", "-b", "0.0.0.0:8080", "src.app:app"]

