#!/bin/bash
set -e

echo "Setting up NVIDIA H100 on Digital Ocean using their recommended approach..."

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
sudo apt-get install -y build-essential

# Install Digital Ocean's recommended NVIDIA packages
echo "Installing NVIDIA packages..."
sudo apt-get install -y linux-headers-$(uname -r)
sudo apt-get install -y nvidia-headless-525-server nvidia-utils-525-server

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
sudo systemctl restart nvidia-persistenced.service

# Install Docker if not already installed
echo "Checking if Docker is installed..."
if ! command -v docker &> /dev/null; then
  echo "Installing Docker..."
  sudo apt-get install -y apt-transport-https ca-certificates curl software-properties-common
  curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -
  sudo add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable"
  sudo apt-get update
  sudo apt-get install -y docker-ce docker-ce-cli containerd.io
fi

# Install NVIDIA Container Toolkit
echo "Installing NVIDIA Container Toolkit..."
distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
curl -s -L https://nvidia.github.io/nvidia-docker/gpgkey | sudo apt-key add -
curl -s -L https://nvidia.github.io/nvidia-docker/$distribution/nvidia-docker.list | sudo tee /etc/apt/sources.list.d/nvidia-docker.list
sudo apt-get update
sudo apt-get install -y nvidia-docker2

# Restart Docker to apply changes
sudo systemctl restart docker

# Create test directory
mkdir -p ~/nvidia-test

# Create a test script to verify NVIDIA drivers
cat << EOF > ~/nvidia-test/test-nvidia.sh
#!/bin/bash
nvidia-smi
docker run --rm --gpus all nvidia/cuda:12.0.1-base-ubuntu22.04 nvidia-smi
EOF

chmod +x ~/nvidia-test/test-nvidia.sh

echo "Testing NVIDIA drivers and Docker..."
~/nvidia-test/test-nvidia.sh || echo "NVIDIA test failed. Please reboot the system and try again."

echo "Installation completed! To verify everything is working correctly, reboot and run: ~/nvidia-test/test-nvidia.sh"
echo "Next steps: Run ./deploy-h100.sh to deploy the Hunyuan application" 