#!/bin/bash

# Create script to download Hunyuan model
cat > download_hunyuan.sh << 'EOF'
#!/bin/bash
set -e

# Set output directory for models
OUTPUT_DIR="$PWD/hunyuan_models"
mkdir -p "$OUTPUT_DIR"

echo "==== Hunyuan Video Model Downloader ===="
echo "Will download to: $OUTPUT_DIR"

# Check if huggingface_hub is installed
if ! pip show huggingface_hub > /dev/null 2>&1; then
  echo "Installing huggingface_hub..."
  pip install huggingface_hub
fi

# Check for HF token
if [ -z "$HF_TOKEN" ]; then
  echo "Warning: HF_TOKEN not set. You might not be able to download the model if it's gated."
  echo "Get a token from https://huggingface.co/settings/tokens"
  read -p "Enter your Hugging Face token (or press Enter to try without): " token
  if [ -n "$token" ]; then
    export HF_TOKEN="$token"
  fi
fi

echo "Downloading Hunyuan Video model..."
python -c "
from huggingface_hub import snapshot_download
import os

token = os.environ.get('HF_TOKEN')
output_dir = '$OUTPUT_DIR'

try:
    snapshot_download(
        repo_id='tencent/HunyuanVideo',
        local_dir=output_dir,
        token=token,
        revision='main',
        resume_download=True,
        ignore_patterns=['*.md']
    )
    print('Download completed successfully!')
except Exception as e:
    print(f'Error downloading model: {str(e)}')
"

echo "==== Download Complete ===="
echo "Model files are in: $OUTPUT_DIR"
echo "Check the HunyuanVideo repository for usage instructions: https://huggingface.co/tencent/HunyuanVideo"
EOF

# Make the script executable
chmod +x download_hunyuan.sh

echo "Created download_hunyuan.sh script"
echo "Run it with: ./download_hunyuan.sh"
