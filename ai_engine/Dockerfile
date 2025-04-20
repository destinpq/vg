FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    libsm6 \
    libxext6 \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better layer caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code
COPY . .

# Set environment variables
ENV MODEL_PATH="/app/models"
ENV RESULTS_DIR="/app/results"
ENV PORT=5000
ENV MAX_CONCURRENT_JOBS=2

# Create necessary directories
RUN mkdir -p ${MODEL_PATH} ${RESULTS_DIR}

# Expose the port
EXPOSE ${PORT}

# Run the application
CMD ["python", "hunyuan_video_api.py"] 