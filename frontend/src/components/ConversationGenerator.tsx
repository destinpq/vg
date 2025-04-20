'use client';

import React, { useState, useRef, useEffect } from 'react';
import { Input, Button, Card, Alert, Select, Row, Col, Space, Typography, Switch, Divider } from 'antd';
import { MessageOutlined, UserOutlined, RobotOutlined } from '@ant-design/icons';

// Import our new components
import StatusTracker from './StatusTracker';
import PromptEnhancer from './PromptEnhancer';
import VideoComparison from './VideoComparison';

const { Title, Text } = Typography;
const { TextArea } = Input;
const { Option } = Select;

// Conversation topic suggestions
const TOPIC_SUGGESTIONS = [
  'artificial intelligence ethics',
  'climate change solutions',
  'future of work',
  'space exploration',
  'healthcare innovation',
  'digital privacy'
];

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

export default function ConversationGenerator() {
  // Core parameters
  const [topic, setTopic] = useState('');
  const [durationMinutes, setDurationMinutes] = useState(1);
  const [segmentDuration, setSegmentDuration] = useState(5);
  
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
  const [enhanceTopic, setEnhanceTopic] = useState(true);
  
  // Subtitle style
  const [subtitleStyle, setSubtitleStyle] = useState({
    font_size: 40,
    font_color: 'white',
    bg_color: 'black',
    bg_alpha: 0.5
  });
  
  // Status tracking
  const [logs, setLogs] = useState<LogEntry[]>([]);
  const [estimatedTimeRemaining, setEstimatedTimeRemaining] = useState('');
  
  // Polling state
  const [pollingActive, setPollingActive] = useState(false);
  const pollingIntervalRef = useRef<NodeJS.Timeout | null>(null);

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

  // Handle topic change
  const handleTopicChange = (newTopic: string) => {
    setTopic(newTopic);
  };

  // Enhance topic with AI
  const enhanceTopicWithAI = async (promptTopic: string) => {
    try {
      addLog('Enhancing conversation topic with AI...', 'loading');
      
      // In a real implementation, call the backend for this
      // For now, simulate an enhanced topic
      const baseTopic = promptTopic.trim();
      
      // Add specific aspects to explore
      const enhanced = `${baseTopic}; exploring historical context, current developments, ethical implications, and future possibilities`;
      
      // Simulate AI processing time
      await new Promise(resolve => setTimeout(resolve, 800));
      
      addLog('Topic enhanced successfully', 'success', { original: baseTopic, enhanced });
      
      return {
        enhanced,
        changes: [
          'exploring historical context',
          'current developments',
          'ethical implications',
          'future possibilities'
        ]
      };
    } catch (error) {
      console.error('Error enhancing topic:', error);
      addLog(`Error enhancing topic: ${error}`, 'error');
      throw error;
    }
  };

  // Poll for video status when videoId is available
  useEffect(() => {
    if (!videoId || !pollingActive) return;
    
    addLog('Starting conversation video generation polling', 'info');
    setStatusMessage('Initializing conversation video generation...');
    
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
          addLog('Conversation video generated successfully!', 'success', { videoUrl: data.video_url });
          
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
            const message = `Processing conversation video... ${Math.round(data.progress)}% complete. ${data.message || ''}`;
            setStatusMessage(message);
            
            // Only add log entry if progress changed significantly (5% increments)
            if (Math.floor(data.progress / 5) !== Math.floor(progress / 5)) {
              addLog(message, 'loading');
            }
          } else {
            setStatusMessage('Processing conversation video...');
          }
        } else if (data.status === 'QUEUED' || data.status === 'queued') {
          setStatusMessage('Your conversation video is queued and will start processing soon...');
          addLog('Conversation video generation queued', 'info');
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

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!topic.trim()) {
      setError('Please enter a conversation topic');
      return;
    }

    setIsGenerating(true);
    setError('');
    setVideoUrl('');
    setProgress(0);
    setStatusMessage('Submitting conversation video request...');
    setLogs([]);
    
    try {
      addLog('Starting conversation video generation', 'info');
      addLog(`Topic: ${topic}`, 'prompt');
      addLog(`Duration: ${durationMinutes} minutes`, 'parameter');
      addLog(`Segment duration: ${segmentDuration} seconds`, 'parameter');
      addLog(`Video dimensions: ${videoWidth}x${videoHeight}`, 'parameter');
      
      // Create request payload
      const payload = {
        topic: topic,
        duration_minutes: durationMinutes,
        segment_duration: segmentDuration,
        video_size: [videoHeight, videoWidth],
        subtitle_style: subtitleStyle
      };
      
      addLog('Sending generation request to server', 'loading', payload);
      
      const response = await apiCall('/video/conversation-video', {
        method: 'POST',
        body: JSON.stringify(payload),
      });

      const data = await response.json();
      addLog('Request submitted successfully', 'success', data);
      
      setVideoId(data.video_id);
      setStatusMessage('Request submitted successfully. Starting conversation video generation...');
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
      console.error('Error generating conversation video:', err);
      setIsGenerating(false);
      setStatusMessage('');
      setPollingActive(false);
    }
  };

  // Get generation parameters for metadata display
  const getGenerationParams = () => {
    return {
      Duration: `${durationMinutes} min`,
      Segments: `${segmentDuration}s each`,
      Resolution: `${videoWidth}x${videoHeight}`,
      "Total Segments": Math.floor(durationMinutes * 60 / segmentDuration)
    };
  };

  return (
    <div className="max-w-6xl mx-auto p-6">
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Left column - Input fields */}
        <div className="input-column space-y-6">
          {/* Header and description */}
          <div className="header-section mb-4">
            <Title level={3} className="m-0">Generate AI Conversation Videos</Title>
            <Text type="secondary">
              Create videos of two AI characters having a conversation about any topic with subtitles and lip sync.
            </Text>
          </div>
          
          {/* Topic with PromptEnhancer */}
          <Card title="Step 1: Conversation Topic" className="shadow-sm">
            <PromptEnhancer
              initialPrompt={topic}
              onPromptChange={handleTopicChange}
              enhancePrompt={enhanceTopicWithAI}
              enhanceEnabled={enhanceTopic}
              onEnableChange={setEnhanceTopic}
              suggestions={TOPIC_SUGGESTIONS}
              loading={isGenerating}
              placeholder="Enter a topic for the AI conversation (e.g., 'Climate change and its impact on society')"
            />
          </Card>
          
          {/* Duration & Settings */}
          <Card title="Step 2: Duration & Settings" className="shadow-sm">
            <div className="space-y-4">
              <div>
                <Text strong>Conversation Duration:</Text>
                <Row gutter={16} align="middle" className="mt-2">
                  <Col span={16}>
                    <Select
                      className="w-full"
                      value={durationMinutes}
                      onChange={setDurationMinutes}
                      disabled={isGenerating}
                    >
                      <Option value={0.5}>30 Seconds</Option>
                      <Option value={1}>1 Minute</Option>
                      <Option value={2}>2 Minutes</Option>
                      <Option value={5}>5 Minutes</Option>
                      <Option value={10}>10 Minutes</Option>
                    </Select>
                  </Col>
                  <Col span={8}>
                    <Text type="secondary" className="text-xs">
                      Longer = more time to generate
                    </Text>
                  </Col>
                </Row>
              </div>
              
              <div>
                <Text strong>Segment Duration:</Text>
                <Row gutter={16} align="middle" className="mt-2">
                  <Col span={16}>
                    <Select
                      className="w-full"
                      value={segmentDuration}
                      onChange={setSegmentDuration}
                      disabled={isGenerating}
                    >
                      <Option value={3}>3 Seconds</Option>
                      <Option value={5}>5 Seconds</Option>
                      <Option value={8}>8 Seconds</Option>
                      <Option value={10}>10 Seconds</Option>
                    </Select>
                  </Col>
                  <Col span={8}>
                    <Text type="secondary" className="text-xs">
                      How long each person speaks
                    </Text>
                  </Col>
                </Row>
              </div>
              
              <Divider style={{ margin: '12px 0' }} />
              
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
              
              <div>
                <Text strong>Subtitle Style:</Text>
                <Row gutter={16} className="mt-2">
                  <Col span={8}>
                    <Text className="text-xs">Font Size:</Text>
                    <Select
                      className="w-full"
                      value={subtitleStyle.font_size}
                      onChange={(value) => setSubtitleStyle({...subtitleStyle, font_size: value})}
                      disabled={isGenerating}
                    >
                      <Option value={30}>Small</Option>
                      <Option value={40}>Medium</Option>
                      <Option value={50}>Large</Option>
                    </Select>
                  </Col>
                  <Col span={8}>
                    <Text className="text-xs">Font Color:</Text>
                    <Select
                      className="w-full"
                      value={subtitleStyle.font_color}
                      onChange={(value) => setSubtitleStyle({...subtitleStyle, font_color: value})}
                      disabled={isGenerating}
                    >
                      <Option value="white">White</Option>
                      <Option value="yellow">Yellow</Option>
                      <Option value="black">Black</Option>
                    </Select>
                  </Col>
                  <Col span={8}>
                    <Text className="text-xs">Background:</Text>
                    <Select
                      className="w-full"
                      value={subtitleStyle.bg_alpha}
                      onChange={(value) => setSubtitleStyle({...subtitleStyle, bg_alpha: value})}
                      disabled={isGenerating}
                    >
                      <Option value={0}>None</Option>
                      <Option value={0.3}>Light</Option>
                      <Option value={0.5}>Medium</Option>
                      <Option value={0.8}>Dark</Option>
                    </Select>
                  </Col>
                </Row>
              </div>
            </div>
          </Card>
          
          {/* Generate Button */}
          <div className="flex justify-center mt-6">
            <Button
              type="primary"
              size="large"
              icon={<MessageOutlined />}
              onClick={handleSubmit}
              disabled={isGenerating || !topic.trim()}
              loading={isGenerating}
              className="px-8 py-2 h-auto"
              style={{ borderRadius: '8px', height: '50px', fontSize: '16px' }}
            >
              {isGenerating ? 'Generating...' : 'Generate Conversation'}
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
              prompt={topic}
              parameters={getGenerationParams()}
              estimatedTimeRemaining={estimatedTimeRemaining}
            />
          )}
          
          {/* Video Display */}
          {videoUrl && (
            <VideoComparison
              title="AI Conversation Video"
              videoUrl={videoUrl}
              metaData={getGenerationParams()}
              showImageComparison={false}
            />
          )}
          
          {/* Empty state when no video */}
          {!videoUrl && !isGenerating && !logs.length && (
            <div className="empty-state p-8 bg-gray-50 rounded-lg border border-gray-200 text-center">
              <div className="flex justify-center">
                <UserOutlined style={{ fontSize: '36px', color: '#1890ff', marginRight: '12px' }} />
                <RobotOutlined style={{ fontSize: '36px', color: '#722ed1' }} />
              </div>
              <Title level={4} className="mt-4">Your conversation video will appear here</Title>
              <Text type="secondary">
                Enter a topic, adjust the settings to your preference, and click "Generate Conversation" to create an AI-driven conversation video.
              </Text>
            </div>
          )}
        </div>
      </div>
    </div>
  );
} 