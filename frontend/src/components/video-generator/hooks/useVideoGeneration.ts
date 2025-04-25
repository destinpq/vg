'use client';

import { useState } from 'react';
import { apiCall } from '../api/apiClient';

export const useVideoGeneration = () => {
  const [prompt, setPrompt] = useState('');
  const [videoUrl, setVideoUrl] = useState('');
  const [videoId, setVideoId] = useState('');
  const [isGenerating, setIsGenerating] = useState(false);
  const [error, setError] = useState('');
  const [statusMessage, setStatusMessage] = useState('');
  const [pollingActive, setPollingActive] = useState(false);
  const [progress, setProgress] = useState(0);
  const [eta, setEta] = useState('');
  const [apiCallCount, setApiCallCount] = useState(0);
  const [diffusionStep, setDiffusionStep] = useState('');
  const [totalCost, setTotalCost] = useState(0);
  
  // Advanced settings
  const [duration, setDuration] = useState(5);
  const [quality, setQuality] = useState('high');
  const [useRealistic, setUseRealistic] = useState(true);
  const [humanFocus, setHumanFocus] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!prompt.trim()) return;

    setIsGenerating(true);
    setError('');
    setVideoUrl('');
    setProgress(0);
    setApiCallCount(0);
    setDiffusionStep('');
    setTotalCost(100); // Initial API call costs 100 rupees
    setStatusMessage('Submitting your request...');
    
    try {
      console.log('Submitting prompt:', prompt);
      console.log('Duration:', duration, 'seconds');
      console.log('Quality:', quality);
      console.log('STYLE:', useRealistic ? 'realistic' : 'abstract');
      
      // ALWAYS force Replicate and disable Hunyuan
      const params = new URLSearchParams({
        prompt: prompt.trim(),
        duration: duration.toString(),
        quality: quality,
        style: useRealistic ? 'realistic' : 'abstract',
        force_replicate: 'true',
        use_hunyuan: 'false',
        human_focus: humanFocus ? 'true' : 'false'
      });
      
      console.log('SENDING PARAMETERS:', params.toString());
      
      // Make a GET request with query parameters
      const response = await apiCall(`/video/generate?${params.toString()}`, {
        method: 'GET',
      });

      const data = await response.json();
      console.log('Video generation response:', data);
      
      setVideoId(data.job_id);
      setStatusMessage('Request submitted successfully. Starting video generation...');
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
      console.error('Error generating video:', err);
      setIsGenerating(false);
      setStatusMessage('');
      setPollingActive(false);
    }
  };

  return {
    prompt, setPrompt,
    videoUrl, setVideoUrl,
    videoId, setVideoId,
    isGenerating, setIsGenerating,
    error, setError,
    statusMessage, setStatusMessage,
    pollingActive, setPollingActive,
    progress, setProgress,
    apiCallCount, setApiCallCount,
    diffusionStep, setDiffusionStep,
    totalCost, setTotalCost,
    duration, setDuration,
    quality, setQuality,
    useRealistic, setUseRealistic,
    humanFocus, setHumanFocus,
    handleSubmit
  };
}; 