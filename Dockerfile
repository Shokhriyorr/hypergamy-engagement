FROM python:3.11.9-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Default: run the pipeline on the bundled sample
CMD ["python", "src/main.py", "--config", "config.yaml"]
