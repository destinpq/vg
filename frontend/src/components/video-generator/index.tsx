'use client';

import React, { useState, useRef, useEffect } from 'react';
import { Card, Space, Typography, Tag, Button } from 'antd';
import { QuestionCircleOutlined } from '@ant-design/icons';
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

const { Title } = Typography;

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
    <div className="max-w-4xl mx-auto p-6">
      {/* Cost display badge */}
      <CostBadge totalCost={totalCost} apiCallCount={apiCallCount} />
      
      {/* Replicate mode banner with cost notice */}
      <VideoGeneratorBanner />
      
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
        
        {isGenerating && (
          <VideoProgress 
            totalCost={totalCost}
            apiCallCount={apiCallCount}
            progress={progress}
            statusMessage={statusMessage}
            diffusionStep={diffusionStep}
          />
        )}
        
        {error && (
          <div className="mt-4">
            {error}
          </div>
        )}
        
        {videoUrl && (
          <VideoResult 
            videoUrl={videoUrl}
            totalCost={totalCost}
            setPrompt={setPrompt}
          />
        )}
      </Card>
      
      {showHelpModal && <HumanVideoHelpModal onClose={() => setShowHelpModal(false)} />}
    </div>
  );
} 