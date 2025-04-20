#!/bin/bash
set -e

echo "Installing NVIDIA H100 drivers on Ubuntu 18.04 using NVIDIA runfile method..."

# Remove any existing NVIDIA installations
echo "Removing existing NVIDIA installations..."
sudo apt-get purge -y '*nvidia*' '*cuda*' || true
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
sudo apt-get install -y build-essential dkms linux-headers-$(uname -r) wget

# Download official NVIDIA runfile for Ubuntu 18.04
echo "Downloading NVIDIA runfile for Ubuntu 18.04..."
wget https://developer.download.nvidia.com/compute/cuda/11.8.0/local_installers/cuda_11.8.0_520.61.05_linux.run

# Make runfile executable
chmod +x cuda_11.8.0_520.61.05_linux.run

# Stop services that might interfere with installation
echo "Stopping display services..."
sudo service lightdm stop || true
sudo service gdm stop || true
sudo service docker stop || true

# Run the installer in silent mode with driver only
echo "Installing NVIDIA drivers..."
sudo ./cuda_11.8.0_520.61.05_linux.run --silent --driver --toolkit --no-opengl-libs --override

# Clean up
rm cuda_11.8.0_520.61.05_linux.run

# Install NVIDIA Container Toolkit
echo "Installing NVIDIA Container Toolkit..."
distribution="ubuntu18.04"
curl -s -L https://nvidia.github.io/nvidia-docker/gpgkey | sudo apt-key add -
curl -s -L https://nvidia.github.io/nvidia-docker/$distribution/nvidia-docker.list | sudo tee /etc/apt/sources.list.d/nvidia-docker.list
sudo apt-get update
sudo apt-get install -y nvidia-docker2

# Configure Docker to use NVIDIA runtime
echo "Configuring Docker daemon..."
cat << EOF | sudo tee /etc/docker/daemon.json
{
    "default-runtime": "nvidia",
    "runtimes": {
        "nvidia": {
            "path": "/usr/bin/nvidia-container-runtime",
            "runtimeArgs": []
        }
    }
}
EOF

# Restart Docker
sudo systemctl restart docker || true

# Create test file
echo "Creating test script..."
mkdir -p ~/nvidia-test
cat << EOF > ~/nvidia-test/test-nvidia.sh
#!/bin/bash
echo "NVIDIA driver test:"
nvidia-smi
echo "Docker GPU test:"
docker run --gpus all nvidia/cuda:11.6.2-base-ubuntu18.04 nvidia-smi
EOF
chmod +x ~/nvidia-test/test-nvidia.sh

echo "Installation completed. Please reboot the system to load the drivers:"
echo "sudo reboot"
echo "After reboot, run: ~/nvidia-test/test-nvidia.sh" 