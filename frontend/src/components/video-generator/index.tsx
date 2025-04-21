'use client';

import React, { useState, useRef, useEffect } from 'react';
import { 
  Card, 
  Space, 
  Typography, 
  Tag, 
  Button, 
  Row, 
  Col, 
  Statistic, 
  Divider, 
  Badge,
  Alert
} from 'antd';
import { 
  QuestionCircleOutlined, 
  RocketOutlined, 
  DollarOutlined, 
  ApiOutlined
} from '@ant-design/icons';
import VideoPlayer from '../video-player';
import CostHistory from '../cost-history';

import { VideoGeneratorBanner } from './Banner';
import { VideoForm } from './VideoForm';
import { VideoProgress } from './VideoProgress';
import { VideoResult } from './VideoResult';
import { HumanVideoHelpModal } from './HelpModal';
import { CostBadge } from './CostBadge';
import { useVideoGeneration } from './hooks/useVideoGeneration';
import { usePolling } from './hooks/usePolling';

import './VideoGenerator.css';

const { Title, Text } = Typography;

export default function VideoGenerator() {
  // State management using custom hooks
  const {
    prompt, setPrompt,
    videoUrl, setVideoUrl,
    videoId, setVideoId,
    isGenerating, setIsGenerating,
    error, setError,
    statusMessage, setStatusMessage,
    progress, setProgress,
    duration, setDuration,
    quality, setQuality,
    useRealistic, setUseRealistic,
    humanFocus, setHumanFocus,
    apiCallCount, setApiCallCount,
    diffusionStep, setDiffusionStep,
    totalCost, setTotalCost,
    handleSubmit
  } = useVideoGeneration();

  const [showAdvanced, setShowAdvanced] = useState(false);
  const [showHelpModal, setShowHelpModal] = useState(false);
  const videoRef = useRef<HTMLVideoElement>(null);

  // Set up polling for video status
  usePolling({
    videoId,
    videoUrl,
    isGenerating,
    setProgress,
    setStatusMessage,
    setApiCallCount,
    setTotalCost,
    setVideoUrl,
    setIsGenerating,
    setDiffusionStep,
    setError
  });

  useEffect(() => {
    // Reset the video element when a new video URL is set
    if (videoRef.current && videoUrl) {
      videoRef.current.load();
    }
  }, [videoUrl]);

  return (
    <Row gutter={[0, 24]} className="video-generator-container">
      {/* Cost display in top-right corner */}
      <Col span={24} style={{ display: 'flex', justifyContent: 'flex-end' }}>
        <Badge 
          count={
            <Space size="small">
              <DollarOutlined />
              <span>₹{totalCost}</span>
            </Space>
          } 
          style={{ 
            backgroundColor: '#1890ff',
            fontSize: '14px',
            padding: '4px 12px',
            borderRadius: '16px'
          }}
        />
      </Col>
      
      {/* Main Generator Card */}
      <Col span={24}>
        <Card 
          className="generator-card" 
          bordered={false}
          style={{ 
            boxShadow: '0 4px 12px rgba(0, 0, 0, 0.08)',
            borderRadius: '12px',
            overflow: 'hidden'
          }}
        >
          {/* Banner with replica mode info */}
          <VideoGeneratorBanner />
          
          <div className="card-header" style={{ padding: '16px 0' }}>
            <Row justify="space-between" align="middle">
              <Col>
                <Space size="middle" align="center">
                  <RocketOutlined style={{ fontSize: '28px', color: '#1890ff' }} />
                  <Title level={2} style={{ margin: 0 }}>
                    Video Generator
                  </Title>
                </Space>
              </Col>
              
              <Col>
                <Space size="middle">
                  <Card 
                    size="small" 
                    style={{ 
                      border: '1px solid #f0f0f0',
                      borderRadius: '8px'
                    }}
                  >
                    <Statistic 
                      title={<Space size="small"><ApiOutlined /> API Calls</Space>}
                      value={apiCallCount}
                      valueStyle={{ color: '#1890ff' }}
                    />
                  </Card>
                  
                  <Card 
                    size="small"
                    style={{ 
                      border: '1px solid #f0f0f0',
                      borderRadius: '8px'
                    }}
                  >
                    <Statistic 
                      title={<Space size="small"><DollarOutlined /> Cost</Space>}
                      value={totalCost}
                      prefix="₹"
                      valueStyle={{ color: '#52c41a' }}
                    />
                  </Card>
                  
                  <Button 
                    type="text" 
                    icon={<QuestionCircleOutlined style={{ fontSize: '22px' }} />} 
                    onClick={() => setShowHelpModal(true)}
                    size="large"
                  />
                </Space>
              </Col>
            </Row>
          </div>
          
          <Divider style={{ margin: '0 0 24px 0' }} />
          
          {/* Video Generation Form */}
          <VideoForm 
            prompt={prompt}
            setPrompt={setPrompt}
            duration={duration}
            setDuration={setDuration}
            showAdvanced={showAdvanced}
            setShowAdvanced={setShowAdvanced}
            quality={quality}
            setQuality={setQuality}
            useRealistic={useRealistic}
            setUseRealistic={setUseRealistic}
            humanFocus={humanFocus}
            setHumanFocus={setHumanFocus}
            isGenerating={isGenerating}
            handleSubmit={handleSubmit}
          />
          
          {/* Progress Display */}
          {isGenerating && (
            <div className="progress-section" style={{ marginTop: '24px' }}>
              <VideoProgress 
                totalCost={totalCost}
                apiCallCount={apiCallCount}
                progress={progress}
                statusMessage={statusMessage}
                diffusionStep={diffusionStep}
              />
            </div>
          )}
          
          {/* Error Display */}
          {error && (
            <Alert
              message="Generation Error"
              description={error}
              type="error"
              showIcon
              style={{ marginTop: '24px' }}
            />
          )}
          
          {/* Video Results */}
          {videoUrl && (
            <div className="result-section" style={{ marginTop: '24px' }}>
              <VideoResult 
                videoUrl={videoUrl}
                totalCost={totalCost}
                setPrompt={setPrompt}
              />
            </div>
          )}
        </Card>
      </Col>
      
      {/* Help Modal */}
      {showHelpModal && <HumanVideoHelpModal onClose={() => setShowHelpModal(false)} />}
    </Row>
  );
} 