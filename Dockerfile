# Use an official Python runtime as the base image
FROM python:3.12-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    netcat-traditional \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy project and entrypoint scripts
COPY . /app/
COPY entrypoint.sh /app/entrypoint.sh
COPY railway.sh /app/railway.sh

# Set execute permission for entrypoint scripts
RUN chmod +x /app/entrypoint.sh /app/railway.sh

# Create and set user
RUN useradd -m appuser && chown -R appuser:appuser /app
USER appuser

# Expose port
EXPOSE 8000

# Run application (Railway will use the Procfile, Docker will use this)
CMD ["/app/railway.sh"]
