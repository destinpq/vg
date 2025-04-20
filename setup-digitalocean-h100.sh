#!/bin/bash
set -e

echo "Setting up NVIDIA drivers for Digital Ocean H100 instance..."

# Clean up any existing installations that might cause conflicts
echo "Cleaning up any existing NVIDIA installations..."
sudo apt-get purge -y '*nvidia*' '*cuda*'
sudo apt-get autoremove -y

# Install required packages
echo "Installing dependencies..."
sudo apt-get update
sudo apt-get install -y build-essential linux-headers-$(uname -r)

# Configure GPU drivers repository
echo "Setting up NVIDIA GPU drivers repository..."
distribution=$(. /etc/os-release;echo $ID$VERSION_ID | sed -e 's/\.//g')

# Remove any previous keys to avoid conflicts
sudo rm -f /etc/apt/trusted.gpg.d/cuda*
sudo apt-key del 7fa2af80 2>/dev/null || true

# Add the official CUDA repository and key
wget https://developer.download.nvidia.com/compute/cuda/repos/$distribution/x86_64/cuda-keyring_1.0-1_all.deb
sudo dpkg -i cuda-keyring_1.0-1_all.deb
rm cuda-keyring_1.0-1_all.deb
sudo apt-get update

# Install CUDA and NVIDIA drivers with specific version to avoid mismatches
echo "Installing CUDA and NVIDIA drivers (matching versions)..."
sudo apt-get install -y cuda-drivers-525 cuda-toolkit-12-1

# Create symbolic links to ensure libraries match driver versions
echo "Setting up library symlinks..."
sudo ln -sf /usr/lib/x86_64-linux-gnu/libnvidia-ml.so.1 /usr/lib/x86_64-linux-gnu/libnvidia-ml.so
sudo ln -sf /usr/lib/x86_64-linux-gnu/libcuda.so.1 /usr/lib/x86_64-linux-gnu/libcuda.so

# Set up NVIDIA container toolkit
echo "Installing NVIDIA Container Toolkit..."
distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
curl -fsSL https://nvidia.github.io/libnvidia-container/gpgkey | sudo gpg --dearmor -o /usr/share/keyrings/nvidia-container-toolkit-keyring.gpg
curl -s -L https://nvidia.github.io/nvidia-container-runtime/$distribution/nvidia-container-runtime.list | \
    sudo tee /etc/apt/sources.list.d/nvidia-container-runtime.list
sudo apt-get update
sudo apt-get install -y nvidia-container-toolkit
sudo systemctl restart docker

# Reload udev rules
echo "Reloading udev rules..."
sudo udevadm control --reload-rules && sudo udevadm trigger

# Verify installation
echo "Verifying NVIDIA driver installation..."
sudo ldconfig
nvidia-smi || echo "nvidia-smi failed, but continuing with setup..."

echo "Setting environment variables..."
export PATH=/usr/local/cuda-12.1/bin${PATH:+:${PATH}}
export LD_LIBRARY_PATH=/usr/local/cuda-12.1/lib64${LD_LIBRARY_PATH:+:${LD_LIBRARY_PATH}}
echo 'export PATH=/usr/local/cuda-12.1/bin${PATH:+:${PATH}}' >> ~/.bashrc
echo 'export LD_LIBRARY_PATH=/usr/local/cuda-12.1/lib64${LD_LIBRARY_PATH:+:${LD_LIBRARY_PATH}}' >> ~/.bashrc
source ~/.bashrc

echo "NVIDIA drivers installation completed. Proceeding to deployment..."

# Run deployment script for H100
echo "Running H100 deployment script..."
./deploy-h100.sh 