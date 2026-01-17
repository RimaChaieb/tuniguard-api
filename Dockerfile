# TuniGuard Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y gcc && rm -rf /var/lib/apt/lists/*

# Copy requirements first (caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the app code
COPY . .

# Environment variables
ENV FLASK_APP=run.py
ENV FLASK_ENV=production
EXPOSE 5000

# Run the app
CMD ["python", "run.py"]
