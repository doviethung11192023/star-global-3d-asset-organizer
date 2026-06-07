FROM python:3.12-slim

# Cài đặt system dependencies cho psycopg2 (nếu cần)
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc libpq-dev && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy requirements và cài đặt Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy toàn bộ mã nguồn backend
COPY . .

# Railway tự động gán PORT. Uvicorn lắng nghe trên 0.0.0.0:$PORT
CMD uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}
