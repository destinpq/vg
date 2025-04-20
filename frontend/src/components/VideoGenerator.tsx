'use client';

import React, { useState, useRef, useEffect } from 'react';
import { Input, Button, Progress, Card, Alert, Select, Spin, Slider, Row, Col, Space, Typography, Switch, Modal, Tooltip } from 'antd';
import { CloudUploadOutlined, VideoCameraOutlined, LoadingOutlined, InfoCircleOutlined, QuestionCircleOutlined } from '@ant-design/icons';
import VideoPlayer from './VideoPlayer';

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
      {/* REPLICATE ONLY MODE BANNER */}
      <div className="mb-4 bg-purple-800 text-white p-3 rounded-lg shadow-lg">
        <div className="flex items-center justify-between">
          <div className="flex items-center">
            <span className="text-xl mr-2">🚀</span>
            <h3 className="font-bold text-lg m-0">REPLICATE API ONLY MODE</h3>
          </div>
          <div className="text-xs bg-purple-700 px-2 py-1 rounded">HUNYUAN DISABLED</div>
        </div>
        <p className="text-sm mt-1 mb-0">All video generation uses Replicate's H100 GPU (50 network calls)</p>
      </div>
      
      <Card className="shadow-lg rounded-lg">
        <div className="flex justify-between items-center mb-6">
          <Title level={2} className="m-0">Pika Labs Video Generator</Title>
          <Button 
            type="text" 
            icon={<QuestionCircleOutlined style={{ fontSize: '22px' }} />} 
            onClick={() => setShowHelpModal(true)}
            size="large"
          />
        </div>
        
        <Alert
          message="Premium Pika Labs Video Generation"
          description={
            <div>
              <p className="mb-2">This application uses Pika Labs HD for high-quality video generation. For best results:</p>
              <ol className="list-decimal ml-5">
                <li className="mb-1">Enter a detailed prompt describing what you want to see</li>
                <li className="mb-1">Set your desired duration and quality</li>
                <li className="mb-1">Click the "Generate with Pika Labs" button</li>
              </ol>
            </div>
          }
          type="info"
          showIcon
          className="mb-4"
        />
        
        <div className="space-y-6">
          <div>
            <Text strong>Describe what you want to see:</Text>
            <Input.TextArea
              rows={4}
              value={prompt}
              onChange={(e) => setPrompt(e.target.value)}
              placeholder="Enter a detailed description of the video you want to generate..."
              className="mt-2"
              disabled={isGenerating}
            />
          </div>

          <Row gutter={16}>
            <Col span={12}>
              <Text strong>Video Duration (seconds):</Text>
              <Slider
                min={5}
                max={10}
                onChange={(value) => setDuration(value)}
                value={duration}
                disabled={isGenerating}
                marks={{
                  5: '5s',
                  7: '7s',
                  10: '10s',
                }}
              />
              <Text type="secondary" className="block mt-1 text-xs">
                {humanFocus 
                  ? "Note: Human videos with Pika Labs work best at 5-6 seconds for optimal quality" 
                  : "Pika Labs generates the best quality videos between 5-10 seconds duration"}
              </Text>
            </Col>
            <Col span={12}>
              <Text strong>Video Quality:</Text>
              <Select
                className="w-full mt-2"
                value={quality}
                onChange={(value) => setQuality(value)}
                disabled={isGenerating}
              >
                <Option value="low">Low (Faster)</Option>
                <Option value="medium">Medium</Option>
                <Option value="high">High (Slower)</Option>
              </Select>
            </Col>
          </Row>

          <div>
            <Row gutter={16} className="mt-4">
              <Col span={24}>
                <div className="flex items-center">
                  <Text strong>Human Focus:</Text>
                  <Tooltip title="Click the help icon for tips on generating human videos">
                    <Button 
                      type="text" 
                      icon={<InfoCircleOutlined />} 
                      onClick={() => setShowHelpModal(true)}
                      size="small"
                      className="ml-2 -mt-1"
                    />
                  </Tooltip>
                </div>
                <div className={humanFocus ? "human-focus-enabled p-3" : "human-focus-disabled p-3"}>
                  <div className="flex items-center justify-between">
                    <div>
                      <Switch
                        checked={humanFocus}
                        onChange={(checked) => {
                          setHumanFocus(checked);
                          setUseRealistic(true); // Always use realistic
                          setStatusMessage(checked ? 
                            'Human focus enabled! Your video will prioritize human content.' : 
                            'Human focus disabled. Video will be optimized for general content.');
                          setTimeout(() => setStatusMessage(''), 3000);
                        }}
                        disabled={isGenerating}
                        checkedChildren="ON" 
                        unCheckedChildren="OFF"
                        className="human-focus-switch"
                      />
                      <Text className="ml-3 font-medium">
                        {humanFocus ? '✓ Human Focus Enabled' : 'Human Focus Disabled'}
                      </Text>
                    </div>
                    <Button
                      type={humanFocus ? "default" : "primary"}
                      onClick={() => {
                        setHumanFocus(!humanFocus);
                      }}
                      size="small"
                      disabled={isGenerating}
                    >
                      {humanFocus ? 'Disable' : 'Enable'}
                    </Button>
                  </div>
                </div>
                {humanFocus && (
                  <Alert
                    message="Human Focus Enabled ✓"
                    description="For best results with humans, be specific about what they're doing. Pika Labs excels at creating realistic humans."
                    type="success"
                    showIcon
                    className="mt-2"
                  />
                )}
              </Col>
            </Row>
          </div>
          
          <div className="mt-6 p-4 border-4 border-purple-500 rounded-lg bg-gradient-to-r from-purple-50 to-indigo-50 shadow-lg">
            <h3 className="text-center text-xl font-bold text-purple-800 mb-3">
              🎬 PIKA LABS HD VIDEO GENERATION 🎬
            </h3>
            <Button
              type="primary" 
              onClick={async () => {
                setIsGenerating(true);
                setError('');
                setVideoUrl('');
                setProgress(0);
                setApiCallCount(0); // Reset API call counter
                setDiffusionStep(''); // Reset diffusion step
                setStatusMessage('Generating premium video with Pika Labs...');
                
                try {
                  // Create URL parameters for premium video generation
                  const params = new URLSearchParams({
                    prompt: prompt.trim(),
                    duration: duration.toString(),
                    quality: 'high',
                    style: 'realistic',
                    force_replicate: 'true',    // ALWAYS force Replicate
                    use_hunyuan: 'false',       // ALWAYS disable Hunyuan
                    human_focus: 'true'         // Better results with human focus
                  });
                  
                  console.log('FORCE REPLICATE ENABLED for premium video');
                  
                  // Make GET request with query parameters
                  const response = await apiCall(`/video/generate?${params.toString()}`);
                  const data = await response.json();
                  
                  console.log('Premium video response:', data);
                  
                  if (data.error) {
                    // Use the specific error_message if available, otherwise use the generic error
                    const errorMessage = data.error_message || data.error;
                    setError(`Video Generation Error: ${errorMessage}`);
                    
                    // Show informative message about Pika Labs if available
                    if (data.pika_message) {
                      setStatusMessage(`Note: ${data.pika_message}`);
                    }
                    
                    console.error('Video generation failed:', data);
                    setIsGenerating(false);
                    return;
                  }
                  
                  // Set video ID for status polling
                  setVideoId(data.job_id);
                  setPollingActive(true);
                  setStatusMessage('Starting REPLICATE video generation process (50 network calls)...');
                  
                  // If video is already completed in the response
                  if (data.status === 'completed' && data.video_url) {
                    setVideoUrl(data.video_url);
                    setIsGenerating(false);
                    setStatusMessage('✨ HD VIDEO GENERATED SUCCESSFULLY!');
                    setPollingActive(false);
                  }
                } catch (err: any) {
                  const errorMessage = err.message || 'Unknown error';
                  setError(`An error occurred: ${errorMessage}`);
                  console.error('Error in video generation:', err);
                  setIsGenerating(false);
                  setStatusMessage('');
                }
              }}
              disabled={isGenerating || !prompt.trim()}
              style={{ 
                background: 'linear-gradient(90deg, #6b46c1, #4f46e5)',
                borderColor: '#4338ca', 
                fontWeight: 'bold',
                height: '70px',
                fontSize: '20px',
                boxShadow: '0 4px 14px rgba(79, 70, 229, 0.4)'
              }}
              className="w-full"
            >
              {isGenerating ? 
                <><LoadingOutlined /> GENERATING YOUR VIDEO...</> : 
                '🎥 GENERATE WITH PIKA LABS 🎥'
              }
            </Button>
            <Text className="block text-center mt-3 text-purple-700 font-medium">
              Pika Labs offers cinema-quality video generation with incredible realism
            </Text>
            <Alert 
              message="About Pika Labs"
              description="Pika Labs requires paid API credits on Replicate. Make sure your API key has sufficient credits for premium video generation."
              type="info"
              showIcon
              className="mt-2"
            />
          </div>

          {error && (
            <Alert
              message="Error"
              description={error}
              type="error"
              showIcon
              closable
            />
          )}

          {isGenerating && !videoUrl && (
            <div className="space-y-2">
              <Progress percent={progress} status="active" />
              <Text type="secondary" className="block text-center">{statusMessage}</Text>
              
              {/* Display API call counter and diffusion step information */}
              {diffusionStep && (
                <div className="mt-4 p-3 bg-blue-50 border border-blue-200 rounded">
                  <div className="flex justify-between items-center">
                    <Text strong>Diffusion Progress:</Text> 
                    <Text>{diffusionStep}</Text>
                  </div>
                  <div className="flex justify-between items-center mt-1">
                    <Text strong>API Calls Made:</Text> 
                    <Text>{apiCallCount}</Text>
                  </div>
                  <div className="mt-2">
                    <Text type="secondary">
                      Replicate makes ~50 network calls during video generation, one for each diffusion step.
                    </Text>
                  </div>
                </div>
              )}
            </div>
          )}

          {videoUrl && (
            <div className="mt-6 space-y-4">
              <Title level={4}>Generated Video</Title>
              <div className="border rounded-lg overflow-hidden">
                <video
                  ref={videoRef}
                  controls
                  className="w-full"
                  autoPlay
                  loop
                >
                  <source src={videoUrl} type="video/mp4" />
                  Your browser does not support the video tag.
                </video>
              </div>
              <div className="flex justify-end">
                <Button
                  type="default"
                  icon={<CloudUploadOutlined />}
                  onClick={() => window.open(videoUrl, '_blank')}
                >
                  Download Video
                </Button>
              </div>
            </div>
          )}
        </div>
        <HumanVideoHelpModal />
      </Card>
    </div>
  );
} 