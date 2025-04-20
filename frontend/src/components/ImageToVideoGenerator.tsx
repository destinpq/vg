'use client';

import React, { useState, useRef, useEffect } from 'react';
import { Input, Button, Card, Alert, Select, Slider, Row, Col, Space, Typography, Switch, Tooltip, Upload, Divider } from 'antd';
import { VideoCameraOutlined, PictureOutlined } from '@ant-design/icons';
import type { UploadFile } from 'antd/es/upload/interface';

// Import our new components
import StatusTracker from './status-tracker';
import PromptEnhancer from './prompt-enhancer';
import VideoComparison from './video-comparison';

const { Title, Text } = Typography;
const { Option } = Select;

// Prompt suggestions for different character styles
const PROMPT_SUGGESTIONS = {
  professional: [
    'speaking confidently', 
    'slight head nod', 
    'professional gesture',
    'subtle smile',
    'thoughtful expression'
  ],
  casual: [
    'relaxed posture', 
    'natural smile', 
    'casual hand gesture',
    'friendly expression',
    'nodding in agreement'
  ],
  creative: [
    'expressive hand movements', 
    'animated facial expressions', 
    'enthusiastic gesture',
    'creative pose',
    'dynamic movement'
  ]
};

// Helper function for API calls
const apiCall = async (endpoint: string, options = {}) => {
  // Hard-code the URL to 5556 since the env variable isn't working
  const baseUrl = 'http://localhost:5556';
  const url = `${baseUrl}${endpoint}`;
  
  console.log(`Making API call to: ${url}`);
  
  const defaultOptions = {
    headers: {
      'Content-Type': 'application/json',
      'Accept': 'application/json',
      'Cache-Control': 'no-cache',
    },
    mode: 'cors' as RequestMode,
  };
  
  try {
    const response = await fetch(url, { ...defaultOptions, ...options });
    
    if (!response.ok) {
      const errorText = await response.text();
      throw new Error(`API error: ${response.status} - ${errorText || response.statusText}`);
    }
    
    return response;
  } catch (error) {
    console.error('API call error:', error);
    throw error;
  }
};

// Log entry type for status tracking
interface LogEntry {
  timestamp: string;
  message: string;
  type: 'info' | 'success' | 'error' | 'loading' | 'prompt' | 'parameter';
  data?: any;
}

export default function ImageToVideoGenerator() {
  // Image and description state
  const [imageFile, setImageFile] = useState<UploadFile | null>(null);
  const [imageUrl, setImageUrl] = useState<string>('');
  const [description, setDescription] = useState('');
  
  // Style options
  const [characterStyle, setCharacterStyle] = useState('professional');
  const [environmentStyle, setEnvironmentStyle] = useState('studio');
  
  // Video generation state
  const [videoUrl, setVideoUrl] = useState('');
  const [videoId, setVideoId] = useState('');
  const [isGenerating, setIsGenerating] = useState(false);
  const [error, setError] = useState('');
  const [statusMessage, setStatusMessage] = useState('');
  const [progress, setProgress] = useState(0);
  
  // Advanced settings
  const [videoHeight, setVideoHeight] = useState(720);
  const [videoWidth, setVideoWidth] = useState(1280);
  const [enhanceDescription, setEnhanceDescription] = useState(true);
  
  // Status tracking
  const [logs, setLogs] = useState<LogEntry[]>([]);
  const [estimatedTimeRemaining, setEstimatedTimeRemaining] = useState('');
  
  // Polling state
  const [pollingActive, setPollingActive] = useState(false);
  const pollingIntervalRef = useRef<NodeJS.Timeout | null>(null);

  // Get current prompt suggestions based on selected character style
  const getCurrentSuggestions = () => {
    return PROMPT_SUGGESTIONS[characterStyle as keyof typeof PROMPT_SUGGESTIONS] || PROMPT_SUGGESTIONS.professional;
  };

  // Add a log entry
  const addLog = (message: string, type: LogEntry['type'] = 'info', data?: any) => {
    const newLog: LogEntry = {
      timestamp: new Date().toISOString(),
      message,
      type,
      data
    };
    
    setLogs(prevLogs => [newLog, ...prevLogs]);
  };

  // Handle prompt change
  const handlePromptChange = (newPrompt: string) => {
    setDescription(newPrompt);
  };

  // Enhance prompt with AI
  const enhancePromptWithAI = async (prompt: string) => {
    try {
      addLog('Enhancing prompt with AI...', 'loading');
      
      // In a real implementation, call the backend for this
      // For now, simulate an enhanced prompt
      const basePrompt = prompt.trim();
      const styleDesc = characterStyle === 'professional' 
        ? 'professional appearance in business attire' 
        : characterStyle === 'casual' 
          ? 'casual appearance in everyday clothing'
          : 'creative professional with artistic style';
          
      const envDesc = environmentStyle === 'office'
        ? 'in modern office setting with natural light'
        : environmentStyle === 'outdoor'
          ? 'in natural outdoor setting with soft sunlight'
          : 'in professional studio with perfect lighting';
          
      const enhanced = `${basePrompt}, ${styleDesc}, ${envDesc}, high quality, detailed features, 4K resolution, cinematic`;
      
      // Simulate AI processing time
      await new Promise(resolve => setTimeout(resolve, 800));
      
      addLog('Prompt enhanced successfully', 'success', { original: basePrompt, enhanced });
      
      return {
        enhanced,
        changes: [
          styleDesc,
          envDesc,
          'high quality, detailed features, 4K resolution, cinematic'
        ]
      };
    } catch (error) {
      console.error('Error enhancing prompt:', error);
      addLog(`Error enhancing prompt: ${error}`, 'error');
      throw error;
    }
  };

  // Poll for video status when videoId is available
  useEffect(() => {
    if (!videoId || !pollingActive) return;
    
    addLog('Starting video generation polling', 'info');
    setStatusMessage('Initializing image-to-video generation...');
    
    // Store the video ID for potential 404 handling
    const currentVideoId = videoId;
    
    const pollStatus = async () => {
      try {
        const response = await apiCall(`/video/status/${currentVideoId}`);
        const data = await response.json();
        
        // Update progress if available
        if (data.progress) {
          setProgress(data.progress);
          
          // Calculate estimated time remaining based on progress
          if (data.progress > 0 && data.progress < 100) {
            const elapsedMs = Date.now() - new Date(logs[logs.length - 1]?.timestamp || Date.now()).getTime();
            const totalEstimatedMs = (elapsedMs / data.progress) * 100;
            const remainingMs = totalEstimatedMs - elapsedMs;
            const remainingMinutes = Math.floor(remainingMs / 60000);
            const remainingSeconds = Math.floor((remainingMs % 60000) / 1000);
            
            setEstimatedTimeRemaining(
              `${remainingMinutes}m ${remainingSeconds}s`
            );
          }
        }
        
        if (data.status === 'COMPLETED' || data.status === 'completed') {
          setVideoUrl(data.video_url);
          setIsGenerating(false);
          setStatusMessage('');
          setPollingActive(false);
          setProgress(100);
          addLog('Video generation completed successfully!', 'success', { videoUrl: data.video_url });
          
          if (pollingIntervalRef.current) {
            clearInterval(pollingIntervalRef.current);
            pollingIntervalRef.current = null;
          }
        } else if (data.status === 'FAILED' || data.status === 'failed') {
          setError(`Video generation failed: ${data.error || 'Unknown error'}`);
          setIsGenerating(false);
          setStatusMessage('');
          setPollingActive(false);
          addLog(`Video generation failed: ${data.error || 'Unknown error'}`, 'error');
          
          if (pollingIntervalRef.current) {
            clearInterval(pollingIntervalRef.current);
            pollingIntervalRef.current = null;
          }
        } else if (data.status === 'PROCESSING' || data.status === 'processing') {
          // Use progress information if available
          if (data.progress) {
            const message = `Processing image-to-video... ${Math.round(data.progress)}% complete. ${data.message || ''}`;
            setStatusMessage(message);
            
            // Only add log entry if progress changed significantly (5% increments)
            if (Math.floor(data.progress / 5) !== Math.floor(progress / 5)) {
              addLog(message, 'loading');
            }
          } else {
            setStatusMessage('Processing image-to-video...');
          }
        } else if (data.status === 'QUEUED' || data.status === 'queued') {
          setStatusMessage('Your image-to-video is queued and will start processing soon...');
          addLog('Video generation queued', 'info');
        }
      } catch (err) {
        console.error('Error checking status:', err);
        
        // Check if we already have a video URL
        if (videoUrl) {
          // If we have a URL but got an error, stop polling - video is ready
          setPollingActive(false);
          
          if (pollingIntervalRef.current) {
            clearInterval(pollingIntervalRef.current);
            pollingIntervalRef.current = null;
          }
        } else {
          setStatusMessage('Checking status...');
        }
      }
    };
    
    // Initial poll
    pollStatus();
    
    // Set up polling interval (every 2 seconds)
    pollingIntervalRef.current = setInterval(pollStatus, 2000);
    
    // Cleanup function
    return () => {
      if (pollingIntervalRef.current) {
        clearInterval(pollingIntervalRef.current);
        pollingIntervalRef.current = null;
      }
      setPollingActive(false);
    };
  }, [videoId, pollingActive, videoUrl, logs, progress]);

  // Handle image upload
  const handleImageUpload = ({ file }: any) => {
    if (file.status === 'done') {
      // Get the file path from the server response
      const serverFilePath = file.response.file_path;
      
      addLog('Image uploaded successfully', 'success', { 
        filename: file.name,
        size: file.size,
        path: serverFilePath
      });
      
      // Set the file and URL
      setImageFile(file);
      setImageUrl(URL.createObjectURL(file.originFileObj));
    } else if (file.status === 'error') {
      const errorMsg = 'Image upload failed: ' + (file.error?.message || 'Unknown error');
      setError(errorMsg);
      addLog(errorMsg, 'error');
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!imageFile) {
      setError('Please upload an image');
      return;
    }
    
    if (!description.trim()) {
      setError('Please enter a description');
      return;
    }

    setIsGenerating(true);
    setError('');
    setVideoUrl('');
    setProgress(0);
    setStatusMessage('Submitting image-to-video request...');
    setLogs([]);
    
    try {
      addLog('Starting image-to-video generation', 'info');
      addLog(`Character style: ${characterStyle}`, 'parameter');
      addLog(`Environment style: ${environmentStyle}`, 'parameter');
      addLog(`Video dimensions: ${videoWidth}x${videoHeight}`, 'parameter');
      addLog(`Prompt: ${description}`, 'prompt');
      
      // Get the actual file path from the server response
      const serverFilePath = imageFile.response?.file_path;
      
      if (!serverFilePath) {
        throw new Error('Image upload was not completed properly');
      }
      
      // Create request payload
      const payload = {
        image_path: serverFilePath,
        description: description,
        character_style: characterStyle,
        environment_style: environmentStyle,
        video_size: [videoHeight, videoWidth],
        enhance_description: enhanceDescription
      };
      
      addLog('Sending generation request to server', 'loading', payload);
      
      const response = await apiCall('/video/image-to-video', {
        method: 'POST',
        body: JSON.stringify(payload),
      });

      const data = await response.json();
      addLog('Request submitted successfully', 'success', data);
      
      setVideoId(data.video_id);
      setStatusMessage('Request submitted successfully. Starting image-to-video generation...');
      setPollingActive(true);
      
      // If video is already completed in the response
      if (data.status === 'COMPLETED' && data.video_url) {
        setVideoUrl(data.video_url);
        setIsGenerating(false);
        setStatusMessage('');
        setPollingActive(false);
        addLog('Video generation completed immediately', 'success');
      }
    } catch (err: any) {
      const errorMessage = err.message || 'Unknown error';
      setError(`An error occurred: ${errorMessage}`);
      addLog(`Error: ${errorMessage}`, 'error');
      console.error('Error generating video from image:', err);
      setIsGenerating(false);
      setStatusMessage('');
      setPollingActive(false);
    }
  };

  // Get generation parameters for metadata display
  const getGenerationParams = () => {
    return {
      Style: characterStyle,
      Environment: environmentStyle,
      Resolution: `${videoWidth}x${videoHeight}`,
      Enhanced: enhanceDescription ? 'Yes' : 'No'
    };
  };

  return (
    <div className="max-w-6xl mx-auto p-6">
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Left column - Input fields */}
        <div className="input-column space-y-6">
          {/* Header and description */}
          <div className="header-section mb-4">
            <Title level={3} className="m-0">Transform Images into Dynamic Videos</Title>
            <Text type="secondary">
              Upload an image, describe the motion, and our AI will bring it to life with consistent character appearance.
            </Text>
          </div>
          
          {/* Image Upload */}
          <Card title="Step 1: Upload Image" className="shadow-sm">
            <div className="text-center">
              <Upload
                name="file"
                listType="picture-card"
                className="image-uploader w-full"
                showUploadList={false}
                action="http://localhost:5556/upload/image"
                onChange={handleImageUpload}
                disabled={isGenerating}
              >
                {imageUrl ? (
                  <img src={imageUrl} alt="uploaded" style={{ width: '100%', height: '100%', objectFit: 'cover' }} />
                ) : (
                  <div style={{ padding: '24px' }}>
                    <PictureOutlined style={{ fontSize: 36, color: '#1890ff' }} />
                    <div className="mt-2">Upload Image</div>
                  </div>
                )}
              </Upload>
            </div>
          </Card>
          
          {/* Description with PromptEnhancer */}
          <Card title="Step 2: Describe Motion & Details" className="shadow-sm">
            <PromptEnhancer
              initialPrompt={description}
              onPromptChange={handlePromptChange}
              enhancePrompt={enhancePromptWithAI}
              enhanceEnabled={enhanceDescription}
              onEnableChange={setEnhanceDescription}
              suggestions={getCurrentSuggestions()}
              loading={isGenerating}
              placeholder="Describe the motion and details you want to add (e.g., 'person speaking confidently with subtle hand gestures')"
            />
          </Card>
          
          {/* Style Selection */}
          <Card title="Step 3: Choose Styles" className="shadow-sm">
            <Row gutter={16}>
              <Col span={12}>
                <Text strong>Character Style:</Text>
                <Select
                  className="w-full mt-2"
                  value={characterStyle}
                  onChange={setCharacterStyle}
                  disabled={isGenerating}
                >
                  <Option value="professional">Professional (Business Attire)</Option>
                  <Option value="casual">Casual (Everyday Clothing)</Option>
                  <Option value="creative">Creative (Expressive Style)</Option>
                </Select>
                <Text type="secondary" className="block mt-1 text-xs">
                  Ensures consistent character appearance and motion
                </Text>
              </Col>
              
              <Col span={12}>
                <Text strong>Environment Style:</Text>
                <Select
                  className="w-full mt-2"
                  value={environmentStyle}
                  onChange={setEnvironmentStyle}
                  disabled={isGenerating}
                >
                  <Option value="office">Professional Office</Option>
                  <Option value="outdoor">Natural Outdoor Setting</Option>
                  <Option value="studio">Photography Studio</Option>
                </Select>
                <Text type="secondary" className="block mt-1 text-xs">
                  Ensures consistent background and lighting
                </Text>
              </Col>
            </Row>
            
            <Divider style={{ margin: '16px 0' }} />
            
            <div>
              <Text strong>Video Size:</Text>
              <Row gutter={16} className="mt-2">
                <Col span={12}>
                  <Select
                    className="w-full"
                    value={videoWidth}
                    onChange={setVideoWidth}
                    disabled={isGenerating}
                  >
                    <Option value={1280}>1280px (Width)</Option>
                    <Option value={1920}>1920px (Width)</Option>
                  </Select>
                </Col>
                <Col span={12}>
                  <Select
                    className="w-full"
                    value={videoHeight}
                    onChange={setVideoHeight}
                    disabled={isGenerating}
                  >
                    <Option value={720}>720px (Height)</Option>
                    <Option value={1080}>1080px (Height)</Option>
                  </Select>
                </Col>
              </Row>
            </div>
          </Card>
          
          {/* Generate Button */}
          <div className="flex justify-center mt-6">
            <Button
              type="primary"
              size="large"
              icon={<VideoCameraOutlined />}
              onClick={handleSubmit}
              disabled={isGenerating || !imageFile || !description.trim()}
              loading={isGenerating}
              className="px-8 py-2 h-auto"
              style={{ borderRadius: '8px', height: '50px', fontSize: '16px' }}
            >
              {isGenerating ? 'Generating...' : 'Generate Video'}
            </Button>
          </div>
          
          {/* Error Display */}
          {error && (
            <Alert
              message="Error"
              description={error}
              type="error"
              showIcon
              closable
              onClose={() => setError('')}
            />
          )}
        </div>
        
        {/* Right column - Result display and status */}
        <div className="result-column space-y-6">
          {/* Status Tracker */}
          {(isGenerating || logs.length > 0) && (
            <StatusTracker
              isGenerating={isGenerating}
              progress={progress}
              statusMessage={statusMessage}
              logs={logs}
              prompt={description}
              parameters={getGenerationParams()}
              estimatedTimeRemaining={estimatedTimeRemaining}
            />
          )}
          
          {/* Video Comparison View */}
          {videoUrl && (
            <VideoComparison
              title="AI Animated Result"
              imageUrl={imageUrl}
              videoUrl={videoUrl}
              metaData={getGenerationParams()}
              showImageComparison={!!imageUrl}
            />
          )}
          
          {/* Empty state when no video */}
          {!videoUrl && !isGenerating && !logs.length && (
            <div className="empty-state p-8 bg-gray-50 rounded-lg border border-gray-200 text-center">
              <VideoCameraOutlined style={{ fontSize: '48px', color: '#d9d9d9' }} />
              <Title level={4} className="mt-4">Your generated video will appear here</Title>
              <Text type="secondary">
                Upload an image, describe the motion you want, and click "Generate Video" to create your AI-animated video.
              </Text>
            </div>
          )}
        </div>
      </div>
    </div>
  );
} 