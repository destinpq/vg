#!/bin/bash
set -e

echo "Direct NVIDIA H100 Driver Installation (Ubuntu 22.04, no DKMS)"
echo "=============================================================="

# Clean existing installations
echo "Removing existing NVIDIA installations..."
sudo apt-get purge -y '*nvidia*' '*cuda*' || true
sudo apt-get autoremove -y
sudo apt-get clean

# Install essential dependencies
echo "Installing essential dependencies..."
sudo apt-get update
sudo apt-get install -y build-essential pkg-config libglvnd-dev

# Create directories for driver installation
sudo mkdir -p /opt/nvidia/drivers
cd /opt/nvidia/drivers

# Download and install the NVIDIA driver directly
echo "Downloading NVIDIA driver for Ubuntu 22.04..."
sudo wget https://us.download.nvidia.com/XFree86/Linux-x86_64/525.147.05/NVIDIA-Linux-x86_64-525.147.05.run
sudo chmod +x NVIDIA-Linux-x86_64-525.147.05.run

# Install the driver with --no-kernel-module option
echo "Installing NVIDIA driver without kernel module..."
sudo ./NVIDIA-Linux-x86_64-525.147.05.run --no-kernel-module --silent --no-questions

# Create symlinks
echo "Creating necessary symlinks..."
sudo ln -sf /usr/lib/x86_64-linux-gnu/libnvidia-ml.so.1 /usr/lib/x86_64-linux-gnu/libnvidia-ml.so
sudo ln -sf /usr/lib/x86_64-linux-gnu/libcuda.so.1 /usr/lib/x86_64-linux-gnu/libcuda.so

# Update library cache
sudo ldconfig

# Install NVIDIA Container Toolkit
echo "Installing NVIDIA Container Toolkit..."
distribution="ubuntu22.04"
curl -fsSL https://nvidia.github.io/libnvidia-container/gpgkey | sudo gpg --dearmor -o /usr/share/keyrings/nvidia-container-toolkit-keyring.gpg
curl -s -L https://nvidia.github.io/nvidia-container-runtime/$distribution/nvidia-container-runtime.list | \
    sudo tee /etc/apt/sources.list.d/nvidia-container-runtime.list
sudo apt-get update
sudo apt-get install -y nvidia-container-toolkit

# Create device nodes if they don't exist
echo "Creating device nodes..."
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
echo "Configuring Docker for NVIDIA..."
sudo nvidia-ctk runtime configure --runtime=docker
sudo systemctl restart docker || true

# Create test script
mkdir -p ~/nvidia-test
cat << EOF > ~/nvidia-test/test-h100.sh
#!/bin/bash
# Test NVIDIA driver
echo "Testing NVIDIA driver..."
nvidia-smi

# Test Docker with NVIDIA
echo "Testing Docker with NVIDIA..."
docker run --rm --gpus all nvidia/cuda:12.0.1-base-ubuntu22.04 nvidia-smi
EOF
chmod +x ~/nvidia-test/test-h100.sh

echo "=============================================================="
echo "Installation completed. A reboot is recommended."
echo "After reboot, run: ~/nvidia-test/test-h100.sh"
echo "==============================================================" 