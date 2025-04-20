'use client';

import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './VideoGenerator.css';

// Set API URL to match the backend port
const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:5001';

// Debug mode - set to true to see more console messages
const DEBUG = true;

function VideoGenerator() {
  const [prompt, setPrompt] = useState('');
  const [duration, setDuration] = useState(5);
  const [quality, setQuality] = useState('high');
  const [style, setStyle] = useState('realistic');
  // Force Hunyuan by marking useReplicate as explicitly false
  const [useReplicate, setUseReplicate] = useState(false);
  const [videoId, setVideoId] = useState(null);
  const [status, setStatus] = useState('');
  const [progress, setProgress] = useState(0);
  const [videoUrl, setVideoUrl] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const [gpuInfo, setGpuInfo] = useState(null);

  // Debug logger function
  const logDebug = (message, data) => {
    if (DEBUG) {
      console.log(`[DEBUG] ${message}`, data);
    }
  };

  // Check GPU status on component mount
  useEffect(() => {
    const checkGpuStatus = async () => {
      try {
        logDebug('Checking GPU status at endpoint:', `${API_URL}/video/hunyuan-status`);
        
        // Add proper headers for CORS
        const response = await axios.get(`${API_URL}/video/hunyuan-status`, {
          headers: {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
          }
        });
        
        setGpuInfo(response.data);
        logDebug("GPU info received:", response.data);
      } catch (err) {
        console.error('Error checking GPU status:', err);
        // Set default values instead of error to handle missing endpoint gracefully
        setGpuInfo({
          status: "Unknown",
          gpu_available: false,
          gpu_memory: 'N/A',
          has_enough_memory: false
        });
      }
    };

    checkGpuStatus();
  }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsLoading(true);
    setError('');
    setVideoId(null);
    setVideoUrl('');
    setStatus('');
    setProgress(0);

    try {
      // FORCE Hunyuan usage
      const usingHunyuan = true; // Force true to always use Hunyuan
      
      // Use the specific Hunyuan endpoint 
      const endpoint = `${API_URL}/video/hunyuan-video`;
         
      // Create the Hunyuan parameters
      const params = { 
        prompt,
        duration: parseFloat(duration),
        width: 1280,
        height: 720,
        fps: 24,
        guidance_scale: 6.5
      };
      
      logDebug(`Using Hunyuan endpoint:`, endpoint);
      logDebug('Request params:', params);
      
      // Make the API request with GET and query params
      const response = await axios.get(endpoint, { 
        params, 
        headers: { 'Accept': 'application/json' } 
      });

      logDebug('Video generation response:', response.data);
      
      // Extract the job_id
      const id = response.data.job_id;
      setVideoId(id);
      setStatus('queued');

      // Status endpoint for Hunyuan
      const statusEndpoint = `${API_URL}/video/job-status/${id}`;
      logDebug('Status endpoint:', statusEndpoint);

      // Start polling for status
      const intervalId = setInterval(async () => {
        try {
          const statusResponse = await axios.get(statusEndpoint, {
            headers: { 'Accept': 'application/json' }
          });
          
          const statusData = statusResponse.data;
          logDebug('Status response:', statusData);
          
          // Handle status format
          const statusValue = statusData.status;
          const progressValue = statusData.progress || 0;
          const urlValue = statusData.video_url;
          
          setStatus(statusValue);
          setProgress(progressValue);
          
          if (urlValue) {
            setVideoUrl(urlValue);
          }

          // Stop polling if the video is completed or failed
          const isCompleted = statusValue === 'completed' || statusValue === 'COMPLETED';
          const isFailed = statusValue === 'failed' || statusValue === 'FAILED';
          
          if (isCompleted || isFailed) {
            clearInterval(intervalId);
            setIsLoading(false);
          }
        } catch (err) {
          console.error('Error checking status:', err);
          clearInterval(intervalId);
          setIsLoading(false);
          setError('Error checking video status');
        }
      }, 2000);
    } catch (err) {
      console.error('Error generating video:', err);
      setIsLoading(false);
      setError(`Error: ${err.message || 'Error connecting to server'}`);
    }
  };

  return (
    <div className="video-generator">
      <h1>AI Video Generator (Tencent Hunyuan)</h1>
      
      {gpuInfo && (
        <div className="gpu-info">
          <h3>GPU Status</h3>
          <p>
            <strong>Status:</strong> {gpuInfo.status}
            <br />
            <strong>GPU Available:</strong> {gpuInfo.gpu_available ? 'Yes' : 'No'}
            {gpuInfo.gpu_available && (
              <>
                <br />
                <strong>GPU Memory:</strong> {gpuInfo.gpu_memory}
                <br />
                <strong>Has Enough Memory:</strong> {gpuInfo.has_enough_memory ? 'Yes' : 'No'}
              </>
            )}
          </p>
        </div>
      )}
      
      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label htmlFor="prompt">Describe your video:</label>
          <textarea
            id="prompt"
            value={prompt}
            onChange={(e) => setPrompt(e.target.value)}
            placeholder="A beautiful sunset over the ocean with waves crashing on the shore"
            required
          />
        </div>
        
        <div className="form-group">
          <label htmlFor="duration">Duration (seconds):</label>
          <input
            type="number"
            id="duration"
            min="1"
            max="10"
            value={duration}
            onChange={(e) => setDuration(e.target.value)}
          />
        </div>
        
        {/* Hide quality and style since we're only using Hunyuan */}
        
        <button type="submit" disabled={isLoading} className="generate-button">
          {isLoading ? 'Generating...' : 'Generate Video with Hunyuan'}
        </button>
      </form>
      
      {error && <div className="error">{error}</div>}
      
      {videoId && (
        <div className="result">
          <h3>Generation Status</h3>
          <p><strong>Status:</strong> {status}</p>
          
          {status !== 'completed' && status !== 'failed' && status !== 'COMPLETED' && status !== 'FAILED' && (
            <div className="progress-bar">
              <div className="progress" style={{ width: `${progress}%` }}></div>
              <span>{Math.round(progress)}%</span>
            </div>
          )}
          
          {videoUrl && (
            <div className="video-container">
              <h3>Generated Video</h3>
              <video controls src={videoUrl} width="100%"></video>
              <a href={videoUrl} download className="download-button">Download Video</a>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

export default VideoGenerator; 