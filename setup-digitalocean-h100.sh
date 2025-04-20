#!/bin/bash
set -e

echo "Setting up NVIDIA drivers for Digital Ocean H100 instance..."

# Install required packages
echo "Installing dependencies..."
sudo apt-get update
sudo apt-get install -y build-essential linux-headers-$(uname -r)

# Configure GPU drivers
echo "Setting up NVIDIA GPU drivers..."
sudo apt-key del 7fa2af80 || true
distribution=$(. /etc/os-release;echo $ID$VERSION_ID | sed -e 's/\.//g')
wget https://developer.download.nvidia.com/compute/cuda/repos/$distribution/x86_64/cuda-keyring_1.0-1_all.deb
sudo dpkg -i cuda-keyring_1.0-1_all.deb
rm cuda-keyring_1.0-1_all.deb
sudo apt-get update

# Install CUDA and NVIDIA drivers
echo "Installing CUDA and NVIDIA drivers..."
sudo apt-get install -y cuda-drivers

# Install NVIDIA container toolkit
echo "Installing NVIDIA Container Toolkit..."
distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
curl -s -L https://nvidia.github.io/nvidia-docker/gpgkey | sudo apt-key add -
curl -s -L https://nvidia.github.io/nvidia-docker/$distribution/nvidia-docker.list | sudo tee /etc/apt/sources.list.d/nvidia-docker.list
sudo apt-get update
sudo apt-get install -y nvidia-container-toolkit
sudo systemctl restart docker

# Verify installation
echo "Verifying NVIDIA driver installation..."
nvidia-smi

echo "NVIDIA drivers have been installed. Proceeding to deployment..."

# Run deployment script for H100
echo "Running H100 deployment script..."
./deploy-h100.sh 