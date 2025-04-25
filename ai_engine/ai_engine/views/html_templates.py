"""
HTML templates for the web interface.
"""

INDEX_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>HunyuanVideo Generator</title>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            line-height: 1.6;
        }
        h1 {
            color: #333;
            border-bottom: 1px solid #ddd;
            padding-bottom: 10px;
        }
        form {
            background: #f9f9f9;
            border: 1px solid #ddd;
            padding: 20px;
            border-radius: 5px;
            margin-bottom: 20px;
        }
        label {
            display: block;
            margin-bottom: 5px;
            font-weight: bold;
        }
        input, select {
            width: 100%;
            padding: 8px;
            margin-bottom: 15px;
            border: 1px solid #ddd;
            border-radius: 4px;
            box-sizing: border-box;
        }
        input[type="checkbox"] {
            width: auto;
        }
        button {
            background-color: #4CAF50;
            color: white;
            padding: 10px 15px;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            font-size: 16px;
        }
        button:hover {
            background-color: #45a049;
        }
        .status-container {
            margin-top: 20px;
            padding: 15px;
            border: 1px solid #ddd;
            border-radius: 5px;
            display: none;
        }
        .video-container {
            margin-top: 20px;
            display: none;
        }
        video {
            max-width: 100%;
            height: auto;
        }
        #status {
            font-weight: bold;
        }
        .hidden {
            display: none;
        }
        .queue-info {
            background-color: #f8f9fa;
            padding: 10px;
            border-radius: 5px;
            margin-bottom: 20px;
            font-size: 14px;
        }
        .gpu-info {
            background-color: #f0f8ff;
            padding: 10px;
            border-radius: 5px;
            margin-bottom: 20px;
            font-size: 14px;
        }
        .footer {
            margin-top: 50px;
            padding-top: 10px;
            border-top: 1px solid #ddd;
            font-size: 12px;
            color: #666;
            text-align: center;
        }
    </style>
</head>
<body>
    <h1>HunyuanVideo Generator</h1>
    
    <div id="gpuInfo" class="gpu-info">
        <h3>GPU Status</h3>
        <p>Status: <span id="gpuStatus">Loading...</span></p>
    </div>
    
    <div id="queueInfo" class="queue-info">
        <h3>Queue Status</h3>
        <p>Current queue: <span id="queueStatus">Checking...</span></p>
    </div>
    
    <form id="generationForm">
        <div>
            <label for="prompt">Text Prompt:</label>
            <input type="text" id="prompt" name="prompt" required placeholder="A cat walks on the grass, realistic style.">
        </div>
        
        <div>
            <label for="resolution">Resolution:</label>
            <select id="resolution" name="resolution">
                <option value="1920x1080">1920x1080 (Full HD) - High Quality</option>
                <option value="1280x720" selected>1280x720 (HD) - Good Balance</option>
                <option value="960x544">960x544 (SD) - Faster</option>
                <option value="720x720">720x720 (Square) - Social Media</option>
            </select>
        </div>
        
        <div>
            <label for="steps">Inference Steps:</label>
            <select id="steps" name="steps">
                <option value="50">50 - Highest Quality</option>
                <option value="40" selected>40 - Good Balance</option>
                <option value="30">30 - Faster</option>
            </select>
        </div>
        
        <div>
            <label for="seed">Random Seed (optional):</label>
            <input type="number" id="seed" name="seed" placeholder="Leave blank for random">
        </div>
        
        <div>
            <label for="embedded_cfg_scale">Guidance Scale:</label>
            <input type="number" id="embedded_cfg_scale" name="embedded_cfg_scale" value="6.0" step="0.5" min="1" max="15">
        </div>
        
        <div>
            <label>
                <input type="checkbox" id="use_fp8" name="use_fp8" checked>
                Use FP8 (Memory Efficient)
            </label>
        </div>
        
        <button type="submit" id="generateBtn">Generate Video</button>
    </form>
    
    <div id="statusContainer" class="status-container">
        <h3>Generation Status</h3>
        <p>ID: <span id="generationId"></span></p>
        <p>Status: <span id="status">Pending</span></p>
        <p>Queue Position: <span id="queuePosition">-</span></p>
        <div id="errorContainer" class="hidden">
            <p>Error: <span id="errorMessage"></span></p>
        </div>
    </div>
    
    <div id="videoContainer" class="video-container">
        <h3>Generated Video</h3>
        <video id="videoPlayer" controls></video>
        <p>
            <a id="downloadLink" href="#" download>Download Video</a>
        </p>
    </div>
    
    <div class="footer">
        <p>HunyuanVideo Generator - Running on H100 GPU</p>
    </div>
    
    <script>
        // Update queue status periodically
        function updateQueueStatus() {
            fetch('/api/queue-status')
                .then(response => response.json())
                .then(data => {
                    document.getElementById('queueStatus').textContent = 
                        `${data.active_jobs} active, ${data.queued_jobs} in queue`;
                    setTimeout(updateQueueStatus, 5000);
                })
                .catch(error => {
                    console.error('Error fetching queue status:', error);
                    setTimeout(updateQueueStatus, 10000);
                });
        }
        
        // Update GPU status periodically
        function updateGpuStatus() {
            fetch('/api/gpu-status')
                .then(response => response.json())
                .then(data => {
                    let gpuText = "";
                    if (data.gpu_info && typeof data.gpu_info === 'object') {
                        for (const [gpu, info] of Object.entries(data.gpu_info)) {
                            if (info && typeof info === 'object') {
                                gpuText += `${gpu}: ${info.free.toFixed(1)}GB free / ${info.total.toFixed(1)}GB total | `;
                            }
                        }
                    }
                    gpuText += `Active jobs: ${data.active_jobs}, Queue: ${data.queued_jobs}`;
                    document.getElementById('gpuStatus').textContent = gpuText;
                    setTimeout(updateGpuStatus, 5000);
                })
                .catch(error => {
                    console.error('Error fetching GPU status:', error);
                    setTimeout(updateGpuStatus, 10000);
                });
        }
        
        // Start status updates
        updateQueueStatus();
        updateGpuStatus();
        
        document.getElementById('generationForm').addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const statusContainer = document.getElementById('statusContainer');
            const videoContainer = document.getElementById('videoContainer');
            const errorContainer = document.getElementById('errorContainer');
            
            statusContainer.style.display = 'block';
            videoContainer.style.display = 'none';
            errorContainer.classList.add('hidden');
            
            document.getElementById('status').textContent = 'Pending';
            document.getElementById('generateBtn').disabled = true;
            
            // Get form values
            const prompt = document.getElementById('prompt').value;
            const resolution = document.getElementById('resolution').value;
            const [width, height] = resolution.split('x').map(Number);
            const steps = parseInt(document.getElementById('steps').value);
            const seedInput = document.getElementById('seed').value;
            const seed = seedInput ? parseInt(seedInput) : null;
            const embedded_cfg_scale = parseFloat(document.getElementById('embedded_cfg_scale').value);
            const use_fp8 = document.getElementById('use_fp8').checked;
            
            // Create request body
            const requestBody = {
                prompt,
                width,
                height,
                steps,
                embedded_cfg_scale,
                use_fp8
            };
            
            if (seed !== null) {
                requestBody.seed = seed;
            }
            
            try {
                // Send generation request
                const response = await fetch('/api/generate', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify(requestBody)
                });
                
                const data = await response.json();
                
                if (!response.ok) {
                    throw new Error(data.error || 'Failed to start generation');
                }
                
                const generationId = data.id;
                document.getElementById('generationId').textContent = generationId;
                if (data.queue_position !== undefined) {
                    document.getElementById('queuePosition').textContent = data.queue_position;
                }
                
                // Poll for status updates
                const checkStatus = async () => {
                    try {
                        const statusResponse = await fetch(`/api/status/${generationId}`);
                        const statusData = await statusResponse.json();
                        
                        document.getElementById('status').textContent = statusData.status;
                        if (statusData.queue_position !== undefined) {
                            document.getElementById('queuePosition').textContent = statusData.queue_position;
                        }
                        
                        if (statusData.status === 'failed') {
                            errorContainer.classList.remove('hidden');
                            document.getElementById('errorMessage').textContent = statusData.error || 'Unknown error';
                            document.getElementById('generateBtn').disabled = false;
                            return;
                        }
                        
                        if (statusData.status === 'completed') {
                            // Show video
                            videoContainer.style.display = 'block';
                            const videoPlayer = document.getElementById('videoPlayer');
                            const downloadLink = document.getElementById('downloadLink');
                            
                            videoPlayer.src = `/api/video/${generationId}`;
                            downloadLink.href = `/api/video/${generationId}`;
                            downloadLink.download = `hunyuan_video_${generationId}.mp4`;
                            
                            document.getElementById('generateBtn').disabled = false;
                            return;
                        }
                        
                        // Keep polling if still in progress
                        setTimeout(checkStatus, 2000);
                    } catch (error) {
                        console.error('Error checking status:', error);
                        document.getElementById('status').textContent = 'Error checking status';
                        document.getElementById('generateBtn').disabled = false;
                    }
                };
                
                checkStatus();
                
            } catch (error) {
                console.error('Error submitting generation:', error);
                document.getElementById('status').textContent = 'Error';
                errorContainer.classList.remove('hidden');
                document.getElementById('errorMessage').textContent = error.message;
                document.getElementById('generateBtn').disabled = false;
            }
        });
    </script>
</body>
</html>
""" 