FROM nvidia/cuda:12.1.1-cudnn8-devel-ubuntu22.04

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONPATH=/app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    python3-pip python3-dev python3-venv \
    ffmpeg git curl wget \
    libsm6 libxext6 libxrender-dev libgl1-mesa-glx \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Create a working directory
WORKDIR /app

# Set up Python virtual environment
RUN python3 -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Upgrade pip and install Python dependencies
RUN pip install --upgrade pip setuptools wheel

# Install backend Python dependencies
COPY backend/requirements.txt /app/backend-requirements.txt
RUN pip install --no-cache-dir -r backend-requirements.txt

# Install additional AI engine requirements
COPY ai_engine/requirements.txt /app/ai_engine-requirements.txt
RUN pip install --no-cache-dir -r ai_engine-requirements.txt

# Install torch with CUDA support for H100
RUN pip install --no-cache-dir torch torchvision torchaudio --extra-index-url https://download.pytorch.org/whl/cu121

# Copy the backend code
COPY backend/ /app/backend/
COPY ai_engine/ /app/ai_engine/
COPY models/ /app/models/
COPY main.py /app/
COPY run_server.py /app/

# Create necessary directories
RUN mkdir -p /app/output /app/outputs

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
CMD ["python", "main.py"] 