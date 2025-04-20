'use client';

import React, { useState, useRef, useEffect } from 'react';
import { Input, Button, Progress, Card, Alert, Select, Spin, Slider, Row, Col, Space, Typography, Switch, Modal, Tooltip, Badge, Tag } from 'antd';
import { CloudUploadOutlined, VideoCameraOutlined, LoadingOutlined, InfoCircleOutlined, QuestionCircleOutlined, RocketOutlined } from '@ant-design/icons';
import VideoPlayer from './VideoPlayer';
import CostHistory from './CostHistory';

// FORCE REPLICATE MODE
console.log("🚀 RUNNING IN REPLICATE-ONLY MODE");
console.log("📢 All video generation will use Replicate API exclusively");
console.log("🔒 Hunyuan is completely disabled");

const { Title, Text } = Typography;
const { Option } = Select;

// Helper function for API calls
const apiCall = async (endpoint: string, options = {}) => {
  // Use port 5001 for our backend server
  const baseUrl = 'http://localhost:5001';
  const url = `${baseUrl}${endpoint}`;
  
  console.log(`Making API call to: ${url}`);
  
  const defaultOptions = {
    headers: {
      'Content-Type': 'application/json',
      'Accept': 'application/json',
      'Cache-Control': 'no-cache', // Add cache control headers
    },
    mode: 'cors' as RequestMode,
  };
  
  try {
    console.log('Starting fetch request...');
    const response = await fetch(url, { ...defaultOptions, ...options });
    console.log(`Response status: ${response.status}`);
    
    if (!response.ok) {
      const errorText = await response.text();
      console.error(`API error (${response.status}): ${errorText}`);
      
      // Special handling for 404 errors on status endpoint after completion
      if (response.status === 404 && endpoint.includes('/video/job-status/')) {
        // If the video was already marked as completed, just return gracefully
        if (localStorage.getItem(`video_completed_${endpoint.split('/').pop()}`)) {
          // Create a fake Response object with the expected json method
          const mockResponse = {
            ok: true,
            status: 200,
            statusText: "OK",
            headers: new Headers(),
            json: () => Promise.resolve({ status: 'completed' })
          } as unknown as Response;
          return mockResponse;
        }
      }
      
      throw new Error(`API error: ${response.status} - ${errorText || response.statusText}`);
    }
    
    return response;
  } catch (error) {
    console.error('API call error:', error);
    throw error;
  }
};

export default function VideoGenerator() {
  const [prompt, setPrompt] = useState('');
  const [videoUrl, setVideoUrl] = useState('');
  const [videoId, setVideoId] = useState('');
  const [isGenerating, setIsGenerating] = useState(false);
  const [error, setError] = useState('');
  const [statusMessage, setStatusMessage] = useState('');
  const [pollingActive, setPollingActive] = useState(false);
  const [progress, setProgress] = useState(0);
  const [eta, setEta] = useState('');
  const [apiCallCount, setApiCallCount] = useState(0); // Track number of API calls
  const [diffusionStep, setDiffusionStep] = useState(''); // Track current diffusion step
  const [totalCost, setTotalCost] = useState(0); // Track total cost (100 rupees per call)
  
  // Advanced settings
  const [duration, setDuration] = useState(5);  // 5 seconds default
  const [quality, setQuality] = useState('high');
  const [useRealistic, setUseRealistic] = useState(true); // Default to realistic
  const [humanFocus, setHumanFocus] = useState(false); // Add human focus toggle
  const [showAdvanced, setShowAdvanced] = useState(false);
  const [showHelpModal, setShowHelpModal] = useState(false);

  // Add premium quality state
  const [premiumQuality, setPremiumQuality] = useState(false);

  const videoRef = useRef<HTMLVideoElement>(null);

  // Poll for video status when videoId is available
  useEffect(() => {
    if (!videoId || !pollingActive) return;
    
    setStatusMessage('Initializing video generation...');
    
    // Store the video ID for potential 404 handling
    const currentVideoId = videoId;
    
    const intervalId = setInterval(async () => {
      try {
        // Increment API call counter to show all requests being made
        setApiCallCount(prev => prev + 1);
        // Update total cost (100 rupees per API call)
        setTotalCost(prev => prev + 100);
        
        // Use the new job-status endpoint
        const response = await apiCall(`/video/job-status/${currentVideoId}`);
        const data = await response.json();
        console.log('Video status:', data);
        
        // Update progress if available
        if (data.progress) {
          setProgress(data.progress);
        }
        
        // Update ETA if available
        if (data.estimated_time) {
          setEta(data.estimated_time);
        }
        
        // Extract diffusion step information if available
        if (data.message && data.message.includes("Diffusion step")) {
          try {
            const stepMatch = /Diffusion step (\d+)\/(\d+)/.exec(data.message);
            if (stepMatch) {
              setDiffusionStep(`${stepMatch[1]}/${stepMatch[2]}`);
            }
          } catch (e) {
            console.error("Error parsing diffusion step", e);
          }
        }
        
        if (data.status === 'completed') {
          setVideoUrl(data.video_url);
          setIsGenerating(false);
          setStatusMessage('');
          setPollingActive(false);
          setProgress(100);
          // Mark this video as completed in localStorage to handle 404s later
          localStorage.setItem(`video_completed_${currentVideoId}`, 'true');
          clearInterval(intervalId);
        } else if (data.status === 'failed') {
          setError(`Video generation failed: ${data.message || data.error || 'Unknown error'}`);
          setIsGenerating(false);
          setStatusMessage('');
          setPollingActive(false);
          clearInterval(intervalId);
        } else if (data.status === 'processing') {
          // Use progress information if available
          if (data.progress) {
            // Check if the message contains diffusion step information
            if (data.message && data.message.includes("Diffusion step")) {
              // Show the full detailed message about diffusion steps and network calls
              setStatusMessage(`${data.message}`);
            } else {
              // Regular processing message
              setStatusMessage(`Processing your video... ${Math.round(data.progress)}% complete. ${data.message || ''}`);
            }
          } else {
            setStatusMessage('Processing your video...');
          }
        } else if (data.status === 'queued') {
          setStatusMessage('Your video is queued and will start processing soon...');
        }
      } catch (err) {
        console.error('Error checking status:', err);
        
        // Check if we already have a video URL
        if (videoUrl) {
          // If we have a URL but got an error, stop polling - video is ready
          setPollingActive(false);
          clearInterval(intervalId);
        } else {
          setStatusMessage('Checking status...');
        }
      }
    }, 2000);
    
    return () => {
      clearInterval(intervalId);
      setPollingActive(false);
    };
  }, [videoId, pollingActive, videoUrl]);

  useEffect(() => {
    // Reset the video element when a new video URL is set
    if (videoRef.current && videoUrl) {
      videoRef.current.load();
    }
  }, [videoUrl]);

  const handleSubmit = async (e: React.FormEvent, usePremium: boolean = false) => {
    e.preventDefault();
    if (!prompt.trim()) return;

    setIsGenerating(true);
    setError('');
    setVideoUrl('');
    setProgress(0);
    setApiCallCount(0); // Reset API call counter
    setDiffusionStep(''); // Reset diffusion step
    setTotalCost(100); // Initial API call costs 100 rupees
    setStatusMessage(usePremium ? 
      'Submitting your request with PREMIUM quality...' : 
      'Submitting your request...');
    
    try {
      console.log('Submitting prompt:', prompt);
      console.log('Duration:', duration, 'seconds');
      console.log('Quality:', quality);
      console.log('STYLE:', useRealistic ? 'realistic' : 'abstract');
      console.log('FORCE REPLICATE: true (always enabled)');
      
      // ALWAYS force Replicate and disable Hunyuan
      const params = new URLSearchParams({
        prompt: prompt.trim(),
        duration: duration.toString(),
        quality: quality,
        style: useRealistic ? 'realistic' : 'abstract',
        force_replicate: 'true',    // ALWAYS force Replicate
        use_hunyuan: 'false',       // ALWAYS disable Hunyuan
        human_focus: 'true'         // Better results with human focus
      });
      
      console.log('SENDING PARAMETERS:', params.toString());
      
      // Make a GET request with query parameters
      const response = await apiCall(`/video/generate?${params.toString()}`, {
        method: 'GET',
      });

      const data = await response.json();
      console.log('Video generation response:', data);
      
      setVideoId(data.job_id); // Updated to use job_id instead of video_id
      setStatusMessage(usePremium ? 
        'Premium request submitted successfully. Starting video generation with REPLICATE...' : 
        'Request submitted successfully. Starting video generation with REPLICATE...');
      setPollingActive(true);
      
      // If video is already completed in the response
      if (data.status === 'completed' && data.video_url) {
        setVideoUrl(data.video_url);
        setIsGenerating(false);
        setStatusMessage(usePremium ? '✨ PREMIUM VIDEO GENERATED!' : '');
        setPollingActive(false);
        localStorage.setItem(`video_completed_${data.job_id}`, 'true');
      }
    } catch (err: any) {
      const errorMessage = err.message || 'Unknown error';
      setError(`An error occurred: ${errorMessage}`);
      console.error('Error generating video:', err);
      setIsGenerating(false);
      setStatusMessage('');
      setPollingActive(false);
    }
  };

  const handleHumanGeneration = async () => {
    if (!prompt.trim()) return;

    setIsGenerating(true);
    setError('');
    setVideoUrl('');
    setProgress(0);
    setApiCallCount(0); // Reset API call counter
    setDiffusionStep(''); // Reset diffusion step
    setStatusMessage('Submitting human video request through REPLICATE...');
    
    try {
      console.log('Submitting human-focused prompt:', prompt);
      console.log('Duration:', duration, 'seconds');
      console.log('FORCE REPLICATE ENABLED for human video');
      
      // Create URL parameters for human-focused video
      const params = new URLSearchParams({
        prompt: prompt.trim(),
        duration: duration.toString(),
        quality: 'high',
        style: 'realistic',
        force_replicate: 'true',    // ALWAYS force Replicate
        use_hunyuan: 'false',       // ALWAYS disable Hunyuan
        human_focus: 'true',
        fps: '24'  // 24fps is better for human videos
      });
      
      // Make GET request with query parameters
      const response = await apiCall(`/video/generate?${params.toString()}`);
      const data = await response.json();
      
      console.log('Human video generation response:', data);
      
      setVideoId(data.job_id);
      setStatusMessage('Request submitted successfully. Starting human video generation with REPLICATE (50 network calls)...');
      setPollingActive(true);
      
      // If video is already completed in the response
      if (data.status === 'completed' && data.video_url) {
        setVideoUrl(data.video_url);
        setIsGenerating(false);
        setStatusMessage('');
        setPollingActive(false);
        localStorage.setItem(`video_completed_${data.job_id}`, 'true');
      }
    } catch (err: any) {
      const errorMessage = err.message || 'Unknown error';
      setError(`An error occurred: ${errorMessage}`);
      console.error('Error generating human video:', err);
      setIsGenerating(false);
      setStatusMessage('');
      setPollingActive(false);
    }
  };

  const testHumanFace = async () => {
    setIsGenerating(true);
    setError('');
    setVideoUrl('');
    setProgress(0);
    setApiCallCount(0); // Reset API call counter
    setDiffusionStep(''); // Reset diffusion step
    setStatusMessage('Testing human face generation with REPLICATE...');
    
    try {
      console.log('FORCE REPLICATE ENABLED for test');
      
      // Create URL parameters for a human face test
      const params = new URLSearchParams({
        prompt: "closeup portrait of a person smiling at camera, high quality, detailed face",
        duration: "5",
        quality: "high",
        style: "realistic",
        force_replicate: "true",    // ALWAYS force Replicate
        use_hunyuan: "false",       // ALWAYS disable Hunyuan
        human_focus: "true"
      });
      
      // Make the request
      const response = await apiCall(`/video/generate?${params.toString()}`);
      const data = await response.json();
      
      // Log the response
      console.log('Human face test response:', data);
      
      if (data.error) {
        setError(`API Error: ${data.error}`);
        console.error('Human face test failed:', data);
        setIsGenerating(false);
        setStatusMessage('');
        return;
      }
      
      // Set the video ID for status polling
      setVideoId(data.job_id);
      setStatusMessage('Human face test submitted through REPLICATE. Tracking 50 network calls...');
      setPollingActive(true);
      
    } catch (err: any) {
      const errorMessage = err.message || 'Unknown error';
      setError(`An error occurred: ${errorMessage}`);
      console.error('Error in human face test:', err);
      setIsGenerating(false);
      setStatusMessage('');
    }
  };

  const ultimateHumanTest = async () => {
    setIsGenerating(true);
    setError('');
    setVideoUrl('');
    setProgress(0);
    setApiCallCount(0); // Reset API call counter
    setDiffusionStep(''); // Reset diffusion step
    setStatusMessage('Running ultimate human test with REPLICATE API...');
    
    try {
      console.log('FORCE REPLICATE ENABLED for ultimate test');
      
      // Create URL parameters for the ultimate human test
      const params = new URLSearchParams({
        prompt: "portrait of a smiling person with detailed facial features, cinematic lighting, 8K, hyperrealistic",
        duration: "5",
        quality: "high",
        style: "realistic",
        force_replicate: "true",    // ALWAYS force Replicate
        use_hunyuan: "false",       // ALWAYS disable Hunyuan
        human_focus: "true"
      });
      
      // Make the direct request to our endpoint
      const response = await apiCall(`/video/generate?${params.toString()}`);
      const data = await response.json();
      
      console.log('Ultimate human test response:', data);
      
      // Set the video ID for status polling
      setVideoId(data.job_id);
      setStatusMessage('Ultimate human test initiated with REPLICATE. Tracking 50 network calls...');
      setPollingActive(true);
      
    } catch (err: any) {
      const errorMessage = err.message || 'Unknown error';
      setError(`An error occurred: ${errorMessage}`);
      console.error('Error in ultimate human test:', err);
      setIsGenerating(false);
      setStatusMessage('');
    }
  };

  const HumanVideoHelpModal = () => (
    <Modal
      title="Tips for Generating Videos with Pika Labs"
      open={showHelpModal}
      onCancel={() => setShowHelpModal(false)}
      footer={[
        <Button key="close" onClick={() => setShowHelpModal(false)}>
          Got it!
        </Button>
      ]}
      width={700}
    >
      <div className="space-y-4">
        <div>
          <h3 className="text-lg font-bold">About Pika Labs</h3>
          <p>Pika Labs is a premium video generation service that creates high-quality, realistic videos from text prompts. It excels at creating human subjects and realistic scenes.</p>
        </div>
        
        <div>
          <h3 className="text-lg font-bold">Creating Effective Prompts</h3>
          <p>For best results with Pika Labs, your prompt should include:</p>
          <ul className="list-disc ml-5">
            <li>Detailed description of subjects (people, objects, scenery)</li>
            <li>Lighting conditions and atmosphere</li>
            <li>Camera angles and movement</li>
            <li>Style references (cinematic, documentary, etc.)</li>
            <li>Quality indicators (high resolution, 8K, detailed, etc.)</li>
          </ul>
        </div>
        
        <div>
          <h3 className="text-lg font-bold">Example Prompts That Work Well:</h3>
          <div className="human-examples">
            <ul className="list-disc ml-5">
              <li>"A cinematic close-up portrait of a young woman with blonde hair smiling at the camera, golden hour lighting, shallow depth of field, shot on ARRI, 8K quality"</li>
              <li>"A businessman in a tailored navy suit walking confidently down a busy city street with glass skyscrapers in the background, cinematic lighting, high detail, telephoto lens"</li>
              <li>"Slow-motion shot of ocean waves crashing against rocky cliffs at sunset, dramatic lighting, hyper-detailed water splashes, cinematic color grading, shot on RED camera"</li>
            </ul>
          </div>
        </div>
        
        <Alert
          message="Important Note"
          description="Pika Labs requires a valid Replicate API token with sufficient credits. Videos are limited to 5-10 seconds for best quality. If you experience issues, verify your API key has sufficient credits."
          type="info"
          showIcon
        />
      </div>
    </Modal>
  );

  return (
    <div className="max-w-4xl mx-auto p-6">
      {/* Cost display badge */}
      <div className="cost-badge">
        <Badge.Ribbon 
          text={
            <span className="cost-value">
              ₹{totalCost}
            </span>
          } 
          color="#722ed1"
        >
          <Card className="text-center" style={{ width: 180 }}>
            <div className="cost-card-content">
              <div className="cost-label font-semibold">Total Server Cost</div>
              <div className="cost-label mt-1">{apiCallCount} API calls</div>
            </div>
          </Card>
        </Badge.Ribbon>
      </div>
      
      {/* Replicate mode banner with cost notice */}
      <div className="mb-4 bg-purple-800 text-white p-3 rounded-lg shadow-lg">
        <div className="flex items-center justify-between">
          <div className="flex items-center">
            <span className="text-xl mr-2">🚀</span>
            <h3 className="font-bold text-lg m-0">REPLICATE API MODE</h3>
          </div>
          <div className="text-xs bg-purple-700 px-2 py-1 rounded">₹100 per API call</div>
        </div>
        <p className="text-sm mt-1 mb-0">All video generation uses Replicate's H100 GPU (cost tracking enabled)</p>
      </div>
      
      <Card className="shadow-lg rounded-lg">
        <div className="flex justify-between items-center mb-6">
          <Title level={2} className="m-0">Video Generator</Title>
          <Space>
            <CostHistory currentSessionCost={totalCost} currentSessionCalls={apiCallCount} />
            <Tag color="purple">Cost: ₹100/request</Tag>
            <Button 
              type="text" 
              icon={<QuestionCircleOutlined style={{ fontSize: '22px' }} />} 
              onClick={() => setShowHelpModal(true)}
              size="large"
            />
          </Space>
        </div>
        
        <Alert
          message="AI Video Generation"
          description={
            <div>
              <p className="mb-2">Generate high-quality AI videos from your text descriptions:</p>
              <ol className="list-decimal ml-5">
                <li className="mb-1">Enter a detailed prompt describing what you want to see</li>
                <li className="mb-1">Set your desired duration and quality</li>
                <li className="mb-1">Click the "Generate Video" button</li>
                <li className="mb-1 text-purple-700 font-semibold">Each server request costs ₹100</li>
              </ol>
            </div>
          }
          type="info"
          showIcon
        />
        
        <div className="mt-6">
          <Text strong>Enter your video description:</Text>
          <Input.TextArea
            rows={4}
            placeholder="Describe the video you want to generate in detail..."
            value={prompt}
            onChange={(e) => setPrompt(e.target.value)}
            disabled={isGenerating}
            className="mt-2"
          />
          
          <div className="flex justify-between items-center mt-4">
            <Button
              type="primary"
              size="large"
              icon={<VideoCameraOutlined />}
              onClick={(e) => handleSubmit(e)}
              loading={isGenerating}
              disabled={!prompt.trim() || isGenerating}
              className="bg-purple-600 hover:bg-purple-700"
            >
              Generate Video
            </Button>
            
            <Space>
              <Text>Duration: {duration}s</Text>
              <Slider
                min={2}
                max={10}
                value={duration}
                onChange={setDuration}
                disabled={isGenerating}
                style={{ width: 120 }}
              />
              
              <Button
                type="link"
                onClick={() => setShowAdvanced(!showAdvanced)}
                disabled={isGenerating}
              >
                {showAdvanced ? 'Hide Advanced' : 'Show Advanced'}
              </Button>
            </Space>
          </div>
          
          {showAdvanced && (
            <div className="grid grid-cols-2 gap-4 mt-4 p-4 bg-gray-50 rounded-lg">
              <div>
                <Text>Quality:</Text>
                <Select
                  style={{ width: '100%' }}
                  value={quality}
                  onChange={setQuality}
                  disabled={isGenerating}
                >
                  <Option value="low">Low (Faster)</Option>
                  <Option value="medium">Medium</Option>
                  <Option value="high">High (Better Quality)</Option>
                </Select>
              </div>
              
              <div>
                <Text>Style Type:</Text>
                <div className="flex items-center mt-2">
                  <Switch
                    checked={useRealistic}
                    onChange={setUseRealistic}
                    disabled={isGenerating}
                  />
                  <Text className="ml-2">{useRealistic ? 'Realistic' : 'Abstract'}</Text>
                </div>
              </div>
              
              <div>
                <Text>Human Focus:</Text>
                <div className="flex items-center mt-2">
                  <Switch
                    checked={humanFocus}
                    onChange={setHumanFocus}
                    disabled={isGenerating}
                  />
                  <Text className="ml-2">{humanFocus ? 'Enabled' : 'Disabled'}</Text>
                </div>
              </div>
            </div>
          )}
          
          {isGenerating && (
            <div className="mt-6">
              <div className="flex justify-between items-center mb-2">
                <Text strong>Generating your video...</Text>
                <div className="flex items-center">
                  <span className="text-purple-600 font-medium mr-2">
                    Cost: ₹{totalCost}
                  </span>
                  <span className="text-gray-500 text-sm">
                    ({apiCallCount} API calls)
                  </span>
                </div>
              </div>
              
              <Progress percent={progress} status="active" />
              
              <div className="mt-2 text-sm text-gray-500 flex justify-between">
                <span>{statusMessage}</span>
                {diffusionStep && <span>Step: {diffusionStep}</span>}
              </div>
            </div>
          )}
          
          {error && (
            <Alert
              className="mt-4"
              message="Error"
              description={error}
              type="error"
              showIcon
            />
          )}
          
          {videoUrl && (
            <div className="mt-6">
              <div className="flex justify-between items-center mb-2">
                <Text strong>Generated Video:</Text>
                <Text type="success">Final Cost: ₹{totalCost}</Text>
              </div>
              <VideoPlayer videoUrl={videoUrl} />
              <div className="mt-4 flex justify-end">
                <Space>
                  <Button type="primary" href={videoUrl} target="_blank">
                    Download
                  </Button>
                  <Button onClick={() => setPrompt('')}>New Video</Button>
                </Space>
              </div>
            </div>
          )}
        </div>
      </Card>
      
      {showHelpModal && <HumanVideoHelpModal />}
    </div>
  );
} 