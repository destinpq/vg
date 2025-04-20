'use client';

import { useState } from 'react';
import { ConversationPayload, SubtitleStyle } from '../types';
import { apiCall } from '../api/apiClient';

interface UseConversationFormProps {
  addLog: (message: string, type: string, data?: any) => void;
  setVideoId: (id: string) => void;
  setVideoUrl: (url: string) => void;
  setStatusMessage: (message: string) => void;
  setPollingActive: (active: boolean) => void;
  setIsGenerating: (generating: boolean) => void;
  setProgress: (progress: number) => void;
  setError: (error: string) => void;
  clearLogs: () => void;
}

export const useConversationForm = ({
  addLog,
  setVideoId,
  setVideoUrl,
  setStatusMessage,
  setPollingActive,
  setIsGenerating,
  setProgress,
  setError,
  clearLogs
}: UseConversationFormProps) => {
  // Core parameters
  const [topic, setTopic] = useState('');
  const [durationMinutes, setDurationMinutes] = useState(1);
  const [segmentDuration, setSegmentDuration] = useState(5);
  
  // Advanced settings
  const [videoHeight, setVideoHeight] = useState(720);
  const [videoWidth, setVideoWidth] = useState(1280);
  
  // Subtitle style
  const [subtitleStyle, setSubtitleStyle] = useState<SubtitleStyle>({
    font_size: 40,
    font_color: 'white',
    bg_color: 'black',
    bg_alpha: 0.5
  });
  
  // Handle topic change
  const handleTopicChange = (newTopic: string) => {
    setTopic(newTopic);
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
    clearLogs();
    
    try {
      addLog('Starting conversation video generation', 'info');
      addLog(`Topic: ${topic}`, 'prompt');
      addLog(`Duration: ${durationMinutes} minutes`, 'parameter');
      addLog(`Segment duration: ${segmentDuration} seconds`, 'parameter');
      addLog(`Video dimensions: ${videoWidth}x${videoHeight}`, 'parameter');
      
      // Create request payload
      const payload: ConversationPayload = {
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

  return {
    topic,
    setTopic,
    durationMinutes,
    setDurationMinutes,
    segmentDuration,
    setSegmentDuration,
    videoHeight,
    setVideoHeight,
    videoWidth,
    setVideoWidth,
    subtitleStyle,
    setSubtitleStyle,
    handleTopicChange,
    getGenerationParams,
    handleSubmit
  };
}; 