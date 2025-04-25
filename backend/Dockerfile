FROM python:3.10-slim

WORKDIR /app

# Install system dependencies including ffmpeg
RUN apt-get update && apt-get install -y \
    ffmpeg \
    curl \
    libsm6 \
    libxext6 \
    netcat \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first to leverage Docker cache
COPY requirements.txt ./

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create required directories
RUN mkdir -p /app/output /app/uploads

# Set environment variables
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# Expose port
EXPOSE 5001

# Set up startup script
COPY start.sh /app/start.sh
RUN chmod +x /app/start.sh

# Start the application using the startup script
CMD ["/app/start.sh", "uvicorn", "app.app:app", "--host", "0.0.0.0", "--port", "5001"] 