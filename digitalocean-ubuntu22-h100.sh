#!/bin/bash
set -e

echo "Setting up NVIDIA H100 on Digital Ocean with Ubuntu 22.04..."

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

# Add NVIDIA repository for Ubuntu 22.04
echo "Adding NVIDIA repository for Ubuntu 22.04..."
wget https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2204/x86_64/cuda-keyring_1.0-1_all.deb
sudo dpkg -i cuda-keyring_1.0-1_all.deb
sudo apt-get update

# Install specific NVIDIA packages for H100 on Ubuntu 22.04
echo "Installing NVIDIA drivers for H100..."
sudo apt-get install -y cuda-drivers-525
sudo apt-get install -y nvidia-utils-525-server

# Set up environment variables
echo "Setting up environment variables..."
echo 'export PATH=/usr/local/cuda/bin${PATH:+:${PATH}}' | sudo tee -a /etc/profile.d/cuda.sh
echo 'export LD_LIBRARY_PATH=/usr/local/cuda/lib64${LD_LIBRARY_PATH:+:${LD_LIBRARY_PATH}}' | sudo tee -a /etc/profile.d/cuda.sh
source /etc/profile.d/cuda.sh

# Install NVIDIA Container Toolkit specifically for Ubuntu 22.04
echo "Installing NVIDIA Container Toolkit for Ubuntu 22.04..."
distribution="ubuntu22.04"
curl -fsSL https://nvidia.github.io/libnvidia-container/gpgkey | sudo gpg --dearmor -o /usr/share/keyrings/nvidia-container-toolkit-keyring.gpg
curl -s -L https://nvidia.github.io/nvidia-container-runtime/$distribution/nvidia-container-runtime.list | \
    sudo tee /etc/apt/sources.list.d/nvidia-container-runtime.list
sudo apt-get update
sudo apt-get install -y nvidia-container-toolkit

# Load necessary kernel modules
echo "Loading NVIDIA kernel modules..."
sudo modprobe nvidia || true
sudo modprobe nvidia_uvm || true

# Set up device nodes
echo "Setting up NVIDIA device nodes..."
if [ ! -e /dev/nvidia0 ]; then
    sudo mknod -m 666 /dev/nvidia0 c 195 0 || true
fi
if [ ! -e /dev/nvidiactl ]; then
    sudo mknod -m 666 /dev/nvidiactl c 195 255 || true
fi
if [ ! -e /dev/nvidia-uvm ]; then
    sudo mknod -m 666 /dev/nvidia-uvm c 243 0 || true
fi

# Configure Docker for NVIDIA
echo "Configuring Docker to use NVIDIA runtime..."
sudo nvidia-ctk runtime configure --runtime=docker
sudo systemctl restart docker || true

# Create test directory
mkdir -p ~/nvidia-test

# Create a test script to verify NVIDIA drivers
cat << EOF > ~/nvidia-test/test-nvidia.sh
#!/bin/bash
echo "NVIDIA driver version:"
nvidia-smi
echo "Testing Docker with NVIDIA:"
docker run --rm --gpus all nvidia/cuda:12.0.1-base-ubuntu22.04 nvidia-smi
EOF

chmod +x ~/nvidia-test/test-nvidia.sh

# Try to run nvidia-smi to see if it works immediately
echo "Testing NVIDIA drivers..."
nvidia-smi || echo "NVIDIA not available yet, a reboot may be required"

# Create a special script for Digital Ocean Droplets
cat << EOF > ~/nvidia-test/digitalocean-fix.sh
#!/bin/bash
echo "Applying Digital Ocean specific fixes for H100..."

# Create symlinks to ensure libraries are found
sudo ln -sf /usr/lib/x86_64-linux-gnu/libnvidia-ml.so.1 /usr/lib/x86_64-linux-gnu/libnvidia-ml.so
sudo ln -sf /usr/lib/x86_64-linux-gnu/libcuda.so.1 /usr/lib/x86_64-linux-gnu/libcuda.so

# Update library cache
sudo ldconfig

# Enable persistence mode
sudo nvidia-smi -pm 1 || true

# Reset the GPU
sudo nvidia-smi --gpu-reset || true

# Try running nvidia-smi
nvidia-smi

# Test Docker with NVIDIA
docker run --rm --gpus all nvidia/cuda:12.0.1-base-ubuntu22.04 nvidia-smi
EOF

chmod +x ~/nvidia-test/digitalocean-fix.sh

echo "===================================================="
echo "Installation completed! A reboot is recommended."
echo "After rebooting, if nvidia-smi still doesn't work, run:"
echo "~/nvidia-test/digitalocean-fix.sh"
echo "====================================================" 