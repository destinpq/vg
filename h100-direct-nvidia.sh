#!/bin/bash
set -e

echo "NVIDIA H100 DIRECT INSTALLATION"
echo "=============================="
echo "This script is specifically designed for Digital Ocean H100 instances"

# Stop any running containers
echo "Stopping any running containers..."
docker ps -q | xargs -r docker stop

# Remove any existing NVIDIA installations completely
echo "Purging ALL existing NVIDIA installations..."
sudo apt-get purge -y '*nvidia*' '*cuda*' '*cudnn*'
sudo apt-get autoremove -y
sudo apt-get clean

# Remove any leftover NVIDIA files
echo "Removing any leftover NVIDIA files..."
sudo rm -rf /etc/apt/sources.list.d/cuda*
sudo rm -rf /etc/apt/sources.list.d/nvidia*
sudo rm -rf /usr/local/cuda*
sudo rm -rf /var/lib/apt/lists/*

# Update the package lists
echo "Updating package lists..."
sudo apt-get update

# Install basic dependencies
echo "Installing basic dependencies..."
sudo apt-get install -y build-essential gcc make dkms

# Install kernel headers
echo "Installing kernel headers..."
sudo apt-get install -y linux-headers-$(uname -r)

# Add the NVIDIA CUDA repository
echo "Adding NVIDIA repository..."
wget https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2204/x86_64/cuda-ubuntu2204.pin
sudo mv cuda-ubuntu2204.pin /etc/apt/preferences.d/cuda-repository-pin-600
wget https://developer.download.nvidia.com/compute/cuda/12.2.1/local_installers/cuda-repo-ubuntu2204-12-2-local_12.2.1-535.86.10-1_amd64.deb
sudo dpkg -i cuda-repo-ubuntu2204-12-2-local_12.2.1-535.86.10-1_amd64.deb
sudo cp /var/cuda-repo-ubuntu2204-12-2-local/cuda-*-keyring.gpg /usr/share/keyrings/
sudo apt-get update

# Install NVIDIA drivers specifically for H100
echo "Installing NVIDIA drivers for H100..."
sudo apt-get install -y cuda-drivers-535

# Install NVIDIA Container Runtime for H100
echo "Installing NVIDIA Container Runtime..."
curl -s -L https://nvidia.github.io/nvidia-container-runtime/gpgkey | \
  sudo apt-key add -
distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
curl -s -L https://nvidia.github.io/nvidia-container-runtime/$distribution/nvidia-container-runtime.list | \
  sudo tee /etc/apt/sources.list.d/nvidia-container-runtime.list
sudo apt-get update
sudo apt-get install -y nvidia-container-runtime

# Configure Docker to use NVIDIA
echo "Configuring Docker to use NVIDIA..."
cat << EOF | sudo tee /etc/docker/daemon.json
{
    "default-runtime": "nvidia",
    "runtimes": {
        "nvidia": {
            "path": "nvidia-container-runtime",
            "runtimeArgs": []
        }
    }
}
EOF

# Restart Docker
echo "Restarting Docker..."
sudo systemctl restart docker

# Add the nvidia-persistenced override
echo "Setting up nvidia-persistenced..."
sudo mkdir -p /etc/systemd/system/nvidia-persistenced.service.d/
cat << EOF | sudo tee /etc/systemd/system/nvidia-persistenced.service.d/override.conf
[Service]
ExecStart=
ExecStart=/usr/bin/nvidia-persistenced --user root
User=root
Group=root
EOF

# Reload systemd
sudo systemctl daemon-reload

# Manually load modules and create nodes
echo "Loading NVIDIA kernel modules..."
sudo modprobe nvidia || true
sudo modprobe nvidia_uvm || true

echo "Creating NVIDIA device nodes..."
sudo ls -la /dev/nvidia* || true
sudo nvidia-modprobe -c 0 -u || true

echo "Installation complete. Reboot now with: sudo reboot"
echo "After reboot, verify the H100 GPU is working with: nvidia-smi"
echo "Then deploy the Hunyuan application." 