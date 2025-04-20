'use client';

import React, { useState } from 'react';
import { Alert, Row, Col } from 'antd';
import StatusTracker from '../status-tracker';
import VideoComparison from '../video-comparison';

// Import hooks
import { useLogging } from './hooks/useLogging';
import { useTopicEnhancement } from './hooks/useTopicEnhancement';
import { useConversationForm } from './hooks/useConversationForm';
import { usePolling } from './hooks/usePolling';

// Import components
import { Header } from './components/Header';
import { ConversationForm } from './components/ConversationForm';
import { EmptyState } from './components/EmptyState';

// Conversation topic suggestions
const TOPIC_SUGGESTIONS = [
  'artificial intelligence ethics',
  'climate change solutions',
  'future of work',
  'space exploration',
  'healthcare innovation',
  'digital privacy'
];

const ConversationGenerator: React.FC = () => {
  // Video generation state
  const [videoUrl, setVideoUrl] = useState('');
  const [videoId, setVideoId] = useState('');
  const [isGenerating, setIsGenerating] = useState(false);
  const [error, setError] = useState('');
  const [statusMessage, setStatusMessage] = useState('');
  const [progress, setProgress] = useState(0);
  const [estimatedTimeRemaining, setEstimatedTimeRemaining] = useState('');
  const [pollingActive, setPollingActive] = useState(false);
  
  // Use our custom hooks
  const { logs, addLog, clearLogs } = useLogging();
  const { enhanceTopic, setEnhanceTopic, enhanceTopicWithAI } = useTopicEnhancement(addLog);
  const conversationForm = useConversationForm({
    addLog,
    setVideoId,
    setVideoUrl,
    setStatusMessage,
    setPollingActive,
    setIsGenerating,
    setProgress,
    setError,
    clearLogs
  });
  
  usePolling({
    videoId,
    videoUrl,
    isGenerating,
    setProgress,
    setStatusMessage,
    setVideoUrl,
    setIsGenerating,
    setError,
    setPollingActive,
    addLog,
    logs,
    estimatedTimeRemaining,
    setEstimatedTimeRemaining
  });

  return (
    <div style={{ maxWidth: '1200px', margin: '0 auto', padding: '24px' }}>
      <Row gutter={24}>
        {/* Left column - Input fields */}
        <Col xs={24} lg={12} style={{ marginBottom: '24px' }}>
          <Header />
          
          <ConversationForm
            topic={conversationForm.topic}
            handleTopicChange={conversationForm.handleTopicChange}
            durationMinutes={conversationForm.durationMinutes}
            setDurationMinutes={conversationForm.setDurationMinutes}
            segmentDuration={conversationForm.segmentDuration}
            setSegmentDuration={conversationForm.setSegmentDuration}
            videoWidth={conversationForm.videoWidth}
            setVideoWidth={conversationForm.setVideoWidth}
            videoHeight={conversationForm.videoHeight}
            setVideoHeight={conversationForm.setVideoHeight}
            subtitleStyle={conversationForm.subtitleStyle}
            setSubtitleStyle={conversationForm.setSubtitleStyle}
            enhanceTopic={enhanceTopic}
            setEnhanceTopic={setEnhanceTopic}
            enhanceTopicWithAI={enhanceTopicWithAI}
            isGenerating={isGenerating}
            handleSubmit={conversationForm.handleSubmit}
            suggestions={TOPIC_SUGGESTIONS}
          />
          
          {/* Error Display */}
          {error && (
            <Alert
              message="Error"
              description={error}
              type="error"
              showIcon
              closable
              onClose={() => setError('')}
              style={{ marginTop: '16px' }}
            />
          )}
        </Col>
        
        {/* Right column - Result display and status */}
        <Col xs={24} lg={12}>
          {/* Status Tracker */}
          {(isGenerating || logs.length > 0) && (
            <StatusTracker
              isGenerating={isGenerating}
              progress={progress}
              statusMessage={statusMessage}
              logs={logs}
              prompt={conversationForm.topic}
              parameters={conversationForm.getGenerationParams()}
              estimatedTimeRemaining={estimatedTimeRemaining}
            />
          )}
          
          {/* Video Display */}
          {videoUrl && (
            <VideoComparison
              title="AI Conversation Video"
              videoUrl={videoUrl}
              metaData={conversationForm.getGenerationParams()}
              showImageComparison={false}
            />
          )}
          
          {/* Empty state when no video */}
          {!videoUrl && !isGenerating && !logs.length && (
            <EmptyState />
          )}
        </Col>
      </Row>
    </div>
  );
};

export default ConversationGenerator; 