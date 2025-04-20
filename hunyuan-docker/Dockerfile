FROM nvidia/cuda:12.1.1-cudnn8-devel-ubuntu22.04

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONPATH=/root/hunyuan-models/HunyuanVideo
ENV FLOW_REVERSE=true
ENV USE_CPU_OFFLOAD=true
ENV HF_HOME=/root/hunyuan-models/huggingface
ENV HF_HUB_DISABLE_SYMLINKS_WARNING=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    python3-pip python3-dev python3-venv \
    git wget curl tmux \
    libsm6 libxext6 libxrender-dev libgl1-mesa-glx \
    ffmpeg ninja-build build-essential \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Create necessary directories
RUN mkdir -p /root/hunyuan-models/HunyuanVideo/ckpts \
    && mkdir -p /root/hunyuan-models/huggingface \
    && mkdir -p /root/output

# Set up working directory
WORKDIR /root/hunyuan-models

# Create and activate virtual environment
RUN python3 -m venv /root/venv
ENV PATH="/root/venv/bin:$PATH"

# Upgrade pip and install base Python packages
RUN pip install --upgrade pip setuptools wheel && \
    pip install torch==2.1.0 torchvision==0.16.0 --extra-index-url https://download.pytorch.org/whl/cu121

# Clone HunyuanVideo repository
RUN git clone https://github.com/zsxkib/HunyuanVideo.git /root/hunyuan-models/HunyuanVideo

# Install HunyuanVideo dependencies
WORKDIR /root/hunyuan-models/HunyuanVideo
RUN pip install -e .

# Install additional dependencies
RUN pip install flask flask-cors requests tqdm huggingface_hub

# Create API wrapper script
COPY hunyuan_api.py /root/hunyuan-models/
COPY download_weights.py /root/hunyuan-models/
COPY entrypoint.sh /root/hunyuan-models/

# Make scripts executable
RUN chmod +x /root/hunyuan-models/entrypoint.sh

# Expose port for API
EXPOSE 8000

# Set entrypoint
ENTRYPOINT ["/root/hunyuan-models/entrypoint.sh"] 