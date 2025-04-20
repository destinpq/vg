#!/usr/bin/env python3
import os
import logging
import argparse
from flask import Flask, request, jsonify, render_template_string
from dotenv import load_dotenv

# Import controllers
from .controllers import ApiController
from .views import INDEX_TEMPLATE

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("HunyuanVideoApp")

def create_app(test_config=None):
    """Create and configure the Flask app"""
    app = Flask(__name__)
    
    # Default configuration
    app.config.from_mapping(
        MODEL_PATH=os.getenv("HUNYUANVIDEO_MODEL_PATH", "/root/.cache/huggingface/hub"),
        FP8_WEIGHTS_PATH=os.getenv("FP8_WEIGHTS_PATH"),
        RESULTS_DIR=os.getenv("RESULTS_DIR", "./results"),
        MAX_CONCURRENT_JOBS=int(os.getenv("MAX_CONCURRENT_JOBS", "1")),
    )
    
    # Override configuration for testing
    if test_config is not None:
        app.config.update(test_config)
    
    # Ensure results directory exists
    os.makedirs(app.config["RESULTS_DIR"], exist_ok=True)
    
    # Initialize controllers
    api_controller = ApiController(
        generation_controller=None  # Let it create its own with environment settings
    )
    
    # Define routes
    @app.route('/')
    def index():
        return render_template_string(INDEX_TEMPLATE)
    
    @app.route('/api/generate', methods=['POST'])
    def generate():
        return jsonify(api_controller.handle_generate(request.json))
    
    @app.route('/api/status/<generation_id>', methods=['GET'])
    def status(generation_id):
        return jsonify(api_controller.handle_status(generation_id))
    
    @app.route('/api/video/<generation_id>', methods=['GET'])
    def video(generation_id):
        return api_controller.handle_video(generation_id)
    
    @app.route('/api/queue-status', methods=['GET'])
    def queue_status():
        return jsonify(api_controller.handle_queue_status())
    
    @app.route('/api/stats', methods=['GET'])
    def stats():
        return jsonify(api_controller.handle_stats())
    
    @app.route('/api/gpu-status', methods=['GET'])
    def gpu_status():
        return jsonify(api_controller.handle_gpu_status())
    
    @app.route('/api/clean-old-videos', methods=['POST'])
    def clean_old_videos():
        return jsonify(api_controller.handle_clean_videos(request.json or {}))
    
    @app.route('/api/resolutions', methods=['GET'])
    def resolutions():
        return jsonify(api_controller.get_supported_resolutions())
    
    return app

def run_app(host="0.0.0.0", port=8080, debug=False, max_concurrent_jobs=None):
    """Run the Flask application"""
    # Override environment settings if specified
    if max_concurrent_jobs is not None:
        os.environ["MAX_CONCURRENT_JOBS"] = str(max_concurrent_jobs)
    
    app = create_app()
    logger.info(f"Starting HunyuanVideo Flask app on http://{host}:{port}")
    logger.info(f"Max concurrent jobs: {os.getenv('MAX_CONCURRENT_JOBS', '1')}")
    app.run(host=host, port=port, debug=debug)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run HunyuanVideo Flask app")
    parser.add_argument("--host", type=str, default="0.0.0.0", help="Host to run on")
    parser.add_argument("--port", type=int, default=8080, help="Port to run on")
    parser.add_argument("--debug", action="store_true", help="Run in debug mode")
    parser.add_argument("--max-concurrent-jobs", type=int, help="Maximum concurrent jobs")
    
    args = parser.parse_args()
    run_app(
        host=args.host,
        port=args.port,
        debug=args.debug,
        max_concurrent_jobs=args.max_concurrent_jobs
    ) 