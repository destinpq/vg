#!/bin/bash
set -e

echo "Installing NVIDIA drivers without DKMS (more reliable for Digital Ocean H100)..."

# Remove any existing NVIDIA installations
echo "Removing existing NVIDIA installations..."
sudo apt-get purge -y '*nvidia*' '*cuda*'
sudo apt-get autoremove -y
sudo apt-get clean

# Fix package system
echo "Fixing package system..."
sudo apt-get update --fix-missing
sudo dpkg --configure -a
sudo apt-get install -f -y

# Install prerequisites
echo "Installing prerequisites..."
sudo apt-get update
sudo apt-get install -y build-essential linux-headers-$(uname -r) wget

# Install runfile drivers directly
echo "Downloading NVIDIA driver runfile (avoiding DKMS)..."
driver_version="525.147.05"
cuda_version="12.1.1"
wget https://developer.download.nvidia.com/compute/cuda/${cuda_version}/local_installers/cuda_${cuda_version}_${driver_version}_linux.run || \
wget https://developer.download.nvidia.com/compute/cuda/12.1.1/local_installers/cuda_12.1.1_525.125.06_linux.run || \
wget https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2204/x86_64/cuda-12-1_12.1.1-1_amd64.deb

# Check which file was downloaded
if [ -f "cuda_${cuda_version}_${driver_version}_linux.run" ]; then
    installer_file="cuda_${cuda_version}_${driver_version}_linux.run"
    install_method="runfile"
elif [ -f "cuda_12.1.1_525.125.06_linux.run" ]; then
    installer_file="cuda_12.1.1_525.125.06_linux.run"
    install_method="runfile"
elif [ -f "cuda-12-1_12.1.1-1_amd64.deb" ]; then
    installer_file="cuda-12-1_12.1.1-1_amd64.deb"
    install_method="deb"
else
    echo "Failed to download NVIDIA installers. Trying alternative approach..."
    install_method="repo"
fi

# Stop potential conflicting services
echo "Stopping potentially conflicting services..."
sudo systemctl stop gdm 2>/dev/null || true
sudo systemctl stop lightdm 2>/dev/null || true
sudo systemctl stop docker 2>/dev/null || true
sudo systemctl stop nvidia-persistenced 2>/dev/null || true

# Install based on which method succeeded
if [ "$install_method" = "runfile" ]; then
    echo "Installing NVIDIA driver from runfile..."
    # Make it executable
    chmod +x "$installer_file"
    # Install driver in silent mode
    sudo ./"$installer_file" --silent --driver --toolkit --no-opengl-libs || echo "Runfile installation failed, continuing..."
    # Clean up
    rm "$installer_file"
elif [ "$install_method" = "deb" ]; then
    echo "Installing NVIDIA driver from deb package..."
    sudo dpkg -i "$installer_file" || echo "Deb installation failed, continuing..."
    sudo apt-get update
    sudo apt-get install -y cuda
    # Clean up
    rm "$installer_file"
else
    echo "Using repository method to install NVIDIA drivers..."
    # Get distribution version
    source /etc/os-release
    # Add NVIDIA package repository
    wget https://developer.download.nvidia.com/compute/cuda/repos/ubuntu$(echo $VERSION_ID | sed 's/\.//')/x86_64/cuda-keyring_1.0-1_all.deb
    sudo dpkg -i cuda-keyring_1.0-1_all.deb
    sudo apt-get update
    sudo apt-get install -y cuda-drivers
    rm cuda-keyring_1.0-1_all.deb
fi

# Set up environment variables
echo "Setting up environment variables..."
echo 'export PATH=/usr/local/cuda/bin${PATH:+:${PATH}}' | sudo tee -a /etc/profile.d/cuda.sh
echo 'export LD_LIBRARY_PATH=/usr/local/cuda/lib64${LD_LIBRARY_PATH:+:${LD_LIBRARY_PATH}}' | sudo tee -a /etc/profile.d/cuda.sh
source /etc/profile.d/cuda.sh

# Install NVIDIA container toolkit
echo "Installing NVIDIA container toolkit..."
source /etc/os-release
curl -fsSL https://nvidia.github.io/libnvidia-container/gpgkey | sudo gpg --dearmor -o /usr/share/keyrings/nvidia-container-toolkit-keyring.gpg
curl -s -L https://nvidia.github.io/nvidia-container-runtime/ubuntu${VERSION_ID}/nvidia-container-runtime.list | \
    sudo tee /etc/apt/sources.list.d/nvidia-container-runtime.list
sudo apt-get update
sudo apt-get install -y nvidia-container-toolkit
sudo nvidia-ctk runtime configure --runtime=docker
sudo systemctl restart docker

# Test NVIDIA driver
echo "Testing NVIDIA driver..."
nvidia-smi || echo "nvidia-smi failed. A reboot may be required."

echo "Installation completed. Please reboot with: sudo reboot" 