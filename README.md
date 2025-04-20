# AI Video Generation with Mochi-1

This application generates videos from text prompts using the Mochi-1 AI model.

## Features

- Generate videos from text descriptions
- Web interface for easy interaction
- Real-time status updates
- Fallback implementation when model files are not available

## System Requirements

- Python 3.10+
- Node.js 18+
- FFmpeg
- For Mochi-1 model: 16GB+ RAM (32GB+ recommended)
- Mac M-series chip with 16GB+ unified memory or NVIDIA GPU with 8GB+ VRAM

## Quick Start

### 1. Clone the repository

```bash
git clone <repository-url>
cd VideoGeneration
```

### 2. Set up the backend

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Set up the frontend

```bash
cd ../frontend
npm install
```

### 4. Setup Model Files (Optional but Recommended)

The application includes a fallback demo implementation, but for actual AI video generation, you need the Mochi-1 model files.

#### Option 1: Download from HuggingFace (Recommended)

1. Go to [Mochi-1 Preview on HuggingFace](https://huggingface.co/genmo/mochi-1-preview)
2. Download the following files:
   - `dit.safetensors` (required)
   - `decoder.safetensors` (required)
3. Place these files in the `models` directory

#### Option 2: Use the Mochi-1 Repository

1. Clone the Mochi-1 repository into the models directory
2. Use the API code provided to generate videos

### 5. Configure Environment

Create environment files:

```bash
cd ../backend
cp .env.example .env

cd ../frontend
cp .env.example .env
```

Edit `.env` files as needed, especially:
- `NEXT_PUBLIC_API_URL=http://localhost:8000` in frontend/.env

### 6. Run the Application

Start the backend:

```bash
cd ../backend
python main.py
```

Start the frontend:

```bash
cd ../frontend
npm run dev
```

Visit `http://localhost:3000` in your browser.

## Running on Mac with Apple Silicon

The application is optimized to run on Mac with Apple Silicon (M1, M2, M3, M4) chips:

1. Make sure you have PyTorch 2.4.0+ installed with MPS support:
   ```bash
   pip install --upgrade torch
   ```

2. The application will automatically detect and use MPS acceleration if available

3. For best performance on an M-series Mac:
   - Close memory-intensive applications before running
   - Ensure you have at least 16GB RAM (32GB+ recommended for the full model)
   - Set the Python environment variable: `export PYTORCH_MPS_HIGH_WATERMARK_RATIO=0.0`

## Troubleshooting

### Missing Model Files

If you see warnings about missing model files:

1. Download the required files from the HuggingFace model repository
2. Place them in the `models` directory

### Video Generation Issues

If video generation fails:

1. Check that FFmpeg is installed: `ffmpeg -version`
2. Ensure you have enough RAM available
3. Try using a shorter prompt or fewer inference steps

### Frontend Connection Issues

If the frontend cannot connect to the backend:

1. Verify that the backend is running
2. Check that `NEXT_PUBLIC_API_URL` in frontend/.env is set correctly
3. Ensure there are no firewall restrictions blocking the connection

## Deployment

For deployment instructions, see [DEPLOYMENT.md](DEPLOYMENT.md).

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgements

- Mochi-1 model by GenMo: [github.com/genmo/mochi](https://github.com/genmo/mochi)
- Based on research from [paper](https://arxiv.org/abs/2401.04092) 