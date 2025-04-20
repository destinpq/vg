# Troubleshooting NVIDIA H100 on Digital Ocean

This guide addresses common issues with NVIDIA H100 GPUs on Digital Ocean droplets.

## Driver/Library Version Mismatch

### Symptom:
```
Failed to initialize NVML: Driver/library version mismatch
NVML library version: 570.133
```

This error occurs when the NVIDIA Management Library (NVML) version doesn't match the installed driver version.

### Solutions:

1. **Complete Driver Purge and Reinstall**

```bash
# Purge all NVIDIA and CUDA packages
sudo apt-get purge -y '*nvidia*' '*cuda*'
sudo apt-get autoremove -y
sudo apt-get clean

# Install specific driver version
sudo apt-get update
sudo apt-get install -y cuda-drivers-525 cuda-toolkit-12-1
```

2. **Fix Library Symlinks**

```bash
# Create correct symbolic links
sudo ln -sf /usr/lib/x86_64-linux-gnu/libnvidia-ml.so.1 /usr/lib/x86_64-linux-gnu/libnvidia-ml.so
sudo ln -sf /usr/lib/x86_64-linux-gnu/libcuda.so.1 /usr/lib/x86_64-linux-gnu/libcuda.so
sudo ldconfig
```

3. **Set Environment Variables**

```bash
export PATH=/usr/local/cuda-12.1/bin${PATH:+:${PATH}}
export LD_LIBRARY_PATH=/usr/local/cuda-12.1/lib64${LD_LIBRARY_PATH:+:${LD_LIBRARY_PATH}}
```

## Docker Can't Access GPU

### Symptom:
```
docker: Error response from daemon: could not select device driver "" with capabilities: [[gpu]].
```

This occurs when Docker can't access the NVIDIA GPU.

### Solutions:

1. **Install NVIDIA Container Toolkit**

```bash
distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
curl -fsSL https://nvidia.github.io/libnvidia-container/gpgkey | sudo gpg --dearmor -o /usr/share/keyrings/nvidia-container-toolkit-keyring.gpg
curl -s -L https://nvidia.github.io/nvidia-container-runtime/$distribution/nvidia-container-runtime.list | \
    sudo tee /etc/apt/sources.list.d/nvidia-container-runtime.list
sudo apt-get update
sudo apt-get install -y nvidia-container-toolkit
sudo systemctl restart docker
```

2. **Verify Docker NVIDIA Runtime**

```bash
# Check if Docker can see the NVIDIA runtime
sudo docker info | grep Runtimes

# Test NVIDIA runtime
docker run --rm --gpus all nvidia/cuda:12.1.1-base-ubuntu22.04 nvidia-smi
```

## Digital Ocean H100 Specific Issues

Digital Ocean's H100 GPU instances may have specific configurations that differ from standard NVIDIA setups:

1. **Ensure GPU Is Attached**:
   Check in the Digital Ocean dashboard that the GPU is properly attached to your droplet.

2. **Use Digital Ocean's CUDA Image**:
   Digital Ocean provides optimized images with pre-installed NVIDIA drivers:
   
   ```bash
   # When creating a new droplet, select the CUDA-enabled image
   # Marketplace > Machine Learning and AI > NVIDIA GPU Optimized VM
   ```

3. **Driver Persistence**:
   Digital Ocean's environment might reset some kernel modules on reboot:
   
   ```bash
   # Add to /etc/rc.local to persist drivers
   sudo nvidia-modprobe -u -c=0
   ```

## Full Manual Fix

If all else fails, use this comprehensive fix:

```bash
# Stop Docker
sudo systemctl stop docker

# Purge all NVIDIA software
sudo apt-get purge -y '*nvidia*' '*cuda*'
sudo apt-get autoremove -y
sudo apt-get clean

# Install CUDA toolkit
distribution=$(. /etc/os-release;echo $ID$VERSION_ID | sed -e 's/\.//g')
wget https://developer.download.nvidia.com/compute/cuda/repos/$distribution/x86_64/cuda-keyring_1.0-1_all.deb
sudo dpkg -i cuda-keyring_1.0-1_all.deb
sudo apt-get update
sudo apt-get install -y cuda-drivers-525 cuda-toolkit-12-1

# Install container toolkit with correct version
curl -fsSL https://nvidia.github.io/libnvidia-container/gpgkey | sudo gpg --dearmor -o /usr/share/keyrings/nvidia-container-toolkit-keyring.gpg
curl -s -L https://nvidia.github.io/nvidia-container-runtime/$(. /etc/os-release;echo $ID$VERSION_ID)/nvidia-container-runtime.list | \
    sudo tee /etc/apt/sources.list.d/nvidia-container-runtime.list
sudo apt-get update
sudo apt-get install -y nvidia-container-toolkit

# Configure Docker to use NVIDIA runtime
sudo nvidia-ctk runtime configure --runtime=docker
sudo systemctl restart docker

# Test NVIDIA driver
sudo ldconfig
nvidia-smi

# Test Docker NVIDIA runtime
docker run --rm --gpus all nvidia/cuda:12.1.1-base-ubuntu22.04 nvidia-smi
```

## Contact Digital Ocean Support

If issues persist, Digital Ocean's support might need to help with H100-specific configurations:

1. Open a ticket at https://cloud.digitalocean.com/support
2. Provide:
   - Droplet ID
   - Output of `nvidia-smi`
   - Output of `docker info`
   - Output of `cat /proc/driver/nvidia/version` 