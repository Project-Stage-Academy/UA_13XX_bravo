# Base image for building dependencies
FROM python:3.11 AS builder

WORKDIR /app

# Ensure logs are displayed immediately
ENV PYTHONUNBUFFERED=1

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# Final image
FROM python:3.11

WORKDIR /app

# Copy installed packages from builder
COPY --from=builder /root/.local /root/.local
ENV PATH="/root/.local/bin:$PATH"

COPY . .

# Expose the port for Django
EXPOSE 8000

# Default command for development
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "UA_13XX_bravo.wsgi:application"]