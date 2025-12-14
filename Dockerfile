# Use official Python runtime as base image
FROM python:3.10-slim

# Set working directory in container
WORKDIR /app

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install -r requirements.txt

# Copy entire project into container
COPY . .

# Create models directory
RUN mkdir -p models

# Expose port for API
EXPOSE 8000

# Default command: run training script
CMD ["python", "src/train.py"]
