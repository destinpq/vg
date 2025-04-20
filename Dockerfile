FROM nvidia/cuda:12.1.1-cudnn8-devel-ubuntu22.04

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DEBIAN_FRONTEND=noninteractive

# Install system dependencies
RUN apt-get update && apt-get install -y \
    python3-pip python3-dev \
    ffmpeg git nodejs npm \
    libsm6 libxext6 libxrender-dev libgl1-mesa-glx \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Create a working directory
WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

# Install additional AI engine requirements
COPY ai_engine/requirements.txt ./ai_engine_requirements.txt
RUN pip3 install --no-cache-dir -r ai_engine_requirements.txt

# Copy the backend code
COPY backend/ ./backend/
COPY ai_engine/ ./ai_engine/
COPY models/ ./models/
COPY main.py .
COPY run_server.py .

# Create necessary directories
RUN mkdir -p output outputs

# Install frontend dependencies and build
COPY frontend/ ./frontend/
WORKDIR /app/frontend
RUN npm install
RUN npm run build

# Set the working directory back to the root directory
WORKDIR /app

# Expose the API port
EXPOSE 5001
EXPOSE 3000

# Run the backend server
CMD ["python3", "main.py"] 