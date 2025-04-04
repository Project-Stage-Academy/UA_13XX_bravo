# Base image for building dependencies
FROM python:3.11 AS builder

WORKDIR /app

# Ensure logs are displayed immediately
ENV PYTHONUNBUFFERED=1

# Install Python dependencies globally
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Final image
FROM python:3.11

# Create a non-root user for running Celery
RUN useradd --create-home --shell /bin/bash celeryuser

WORKDIR /app

# Copy installed packages from builder (system-wide)
COPY --from=builder /usr/local /usr/local

# Copy project files
COPY . .

# Set working directory ownership
RUN chown -R celeryuser:celeryuser /app

# Set working directory ownership
RUN chown -R celeryuser:celeryuser /app \
 && mkdir -p /app/staticfiles \
 && chown -R celeryuser:celeryuser /app/staticfiles


# Expose the port for Django
EXPOSE 8000


