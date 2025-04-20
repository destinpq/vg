#!/bin/bash
set -e

echo "Setting up NVIDIA H100 on Digital Ocean Ubuntu 18.04..."

# Clean existing installations
echo "Cleaning existing NVIDIA installations..."
sudo apt-get purge -y '*nvidia*' '*cuda*' || true
sudo apt-get autoremove -y
sudo apt-get clean

# Update package lists
echo "Updating package lists..."
sudo apt-get update

# Install essential dependencies
echo "Installing essential dependencies..."
sudo apt-get install -y build-essential linux-headers-$(uname -r)

# Add NVIDIA repository for Ubuntu 18.04
echo "Adding NVIDIA repository for Ubuntu 18.04..."
wget https://developer.download.nvidia.com/compute/cuda/repos/ubuntu1804/x86_64/cuda-keyring_1.0-1_all.deb
sudo dpkg -i cuda-keyring_1.0-1_all.deb
sudo apt-get update

# Install specific NVIDIA drivers for Ubuntu 18.04
echo "Installing NVIDIA drivers for H100 on Ubuntu 18.04..."
sudo apt-get install -y cuda-drivers-525
sudo apt-get install -y cuda-runtime-12-0 cuda-toolkit-12-0

# Create nvidia-persistenced service override directory
sudo mkdir -p /etc/systemd/system/nvidia-persistenced.service.d/

# Create override file to ensure nvidia-persistenced runs as root
echo "Creating service override for nvidia-persistenced..."
cat << EOF | sudo tee /etc/systemd/system/nvidia-persistenced.service.d/override.conf
[Service]
ExecStart=
ExecStart=/usr/bin/nvidia-persistenced --user root
User=root
Group=root
EOF

# Reload systemd to apply changes
sudo systemctl daemon-reload
sudo systemctl restart nvidia-persistenced.service || true

# Set up environment variables
echo "Setting up environment variables..."
echo 'export PATH=/usr/local/cuda/bin${PATH:+:${PATH}}' | sudo tee -a /etc/profile.d/cuda.sh
echo 'export LD_LIBRARY_PATH=/usr/local/cuda/lib64${LD_LIBRARY_PATH:+:${LD_LIBRARY_PATH}}' | sudo tee -a /etc/profile.d/cuda.sh
source /etc/profile.d/cuda.sh

# Install NVIDIA Container Toolkit specifically for Ubuntu 18.04
echo "Installing NVIDIA Container Toolkit for Ubuntu 18.04..."
distribution="ubuntu18.04"
curl -s -L https://nvidia.github.io/nvidia-docker/gpgkey | sudo apt-key add -
curl -s -L https://nvidia.github.io/nvidia-docker/$distribution/nvidia-docker.list | sudo tee /etc/apt/sources.list.d/nvidia-docker.list
sudo apt-get update
sudo apt-get install -y nvidia-docker2

# Configure Docker to use NVIDIA runtime
echo "Configuring Docker to use NVIDIA runtime..."
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

# Restart Docker to apply changes
sudo systemctl restart docker || true

# Create test directory
mkdir -p ~/nvidia-test

# Create a test script to verify NVIDIA drivers
cat << EOF > ~/nvidia-test/test-nvidia.sh
#!/bin/bash
echo "NVIDIA driver version:"
nvidia-smi
echo "Testing Docker with NVIDIA:"
docker run --rm --gpus all nvidia/cuda:11.6.2-base-ubuntu20.04 nvidia-smi
EOF

chmod +x ~/nvidia-test/test-nvidia.sh

echo "Testing NVIDIA drivers..."
nvidia-smi || echo "NVIDIA not available yet, a reboot is required"

# Add a convenience setup script for after reboot
cat << EOF > ~/nvidia-test/finish-setup.sh
#!/bin/bash
echo "Loading NVIDIA kernel modules..."
sudo modprobe nvidia
sudo modprobe nvidia_uvm

echo "Testing NVIDIA drivers..."
nvidia-smi

echo "Setting up persistent device nodes..."
sudo nvidia-smi -pm 1

echo "Testing Docker with NVIDIA..."
docker run --rm --gpus all nvidia/cuda:11.6.2-base-ubuntu20.04 nvidia-smi
EOF

chmod +x ~/nvidia-test/finish-setup.sh

echo "===================================================="
echo "Installation completed! A reboot is required."
echo "After rebooting, run: ~/nvidia-test/finish-setup.sh"
echo "===================================================="
echo "Run this command to reboot: sudo reboot" 