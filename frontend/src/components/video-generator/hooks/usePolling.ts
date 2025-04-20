'use client';

import { useEffect } from 'react';
import { apiCall } from '../api/apiClient';

interface UsePollingProps {
  videoId: string;
  videoUrl: string;
  isGenerating: boolean;
  setProgress: (progress: number) => void;
  setStatusMessage: (message: string) => void;
  setApiCallCount: (count: number | ((prev: number) => number)) => void;
  setTotalCost: (cost: number | ((prev: number) => number)) => void;
  setVideoUrl: (url: string) => void;
  setIsGenerating: (isGenerating: boolean) => void;
  setDiffusionStep: (step: string) => void;
  setError: (error: string) => void;
}

export const usePolling = ({
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
  setError,
}: UsePollingProps) => {
  useEffect(() => {
    if (!videoId || !isGenerating) return;
    
    setStatusMessage('Initializing video generation...');
    
    // Store the video ID for potential 404 handling
    const currentVideoId = videoId;
    
    const intervalId = setInterval(async () => {
      try {
        // Increment API call counter to show all requests being made
        setApiCallCount(prev => prev + 1);
        // Update total cost (100 rupees per API call)
        setTotalCost(prev => prev + 100);
        
        // Use the job-status endpoint
        const response = await apiCall(`/video/job-status/${currentVideoId}`);
        const data = await response.json();
        console.log('Video status:', data);
        
        // Update progress if available
        if (data.progress) {
          setProgress(data.progress);
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
          setProgress(100);
          // Mark this video as completed in localStorage to handle 404s later
          localStorage.setItem(`video_completed_${currentVideoId}`, 'true');
          clearInterval(intervalId);
        } else if (data.status === 'failed') {
          setError(`Video generation failed: ${data.message || data.error || 'Unknown error'}`);
          setIsGenerating(false);
          setStatusMessage('');
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
          clearInterval(intervalId);
        } else {
          setStatusMessage('Checking status...');
        }
      }
    }, 2000);
    
    return () => {
      clearInterval(intervalId);
    };
  }, [videoId, videoUrl, isGenerating, setProgress, setStatusMessage, setApiCallCount, 
      setTotalCost, setVideoUrl, setIsGenerating, setDiffusionStep, setError]);
}; 