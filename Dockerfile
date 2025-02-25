# Use the official Python image
FROM python:3.11

# Set the working directory inside the container
WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the project files into the container
COPY . .

RUN mkdir -p /app/staticfiles

# Expose the port for Django
EXPOSE 8000
