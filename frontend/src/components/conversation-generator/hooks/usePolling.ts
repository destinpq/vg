'use client';

import { useEffect, useRef } from 'react';
import { apiCall } from '../api/apiClient';
import { LogEntry } from '../types';

interface UsePollingProps {
  videoId: string;
  videoUrl: string;
  isGenerating: boolean;
  progress?: number;
  setProgress: (progress: number) => void;
  setStatusMessage: (message: string) => void;
  setVideoUrl: (url: string) => void;
  setIsGenerating: (isGenerating: boolean) => void;
  setError: (error: string) => void;
  setPollingActive: (active: boolean) => void;
  addLog: (message: string, type: LogEntry['type'], data?: any) => void;
  logs: LogEntry[];
  estimatedTimeRemaining: string;
  setEstimatedTimeRemaining: (time: string) => void;
}

export const usePolling = (props: UsePollingProps) => {
  const {
    videoId,
    videoUrl,
    isGenerating,
    progress,
    setProgress,
    setStatusMessage,
    setVideoUrl,
    setIsGenerating,
    setError,
    setPollingActive,
    addLog,
    logs
  } = props;
  
  const pollingIntervalRef = useRef<NodeJS.Timeout | null>(null);

  useEffect(() => {
    if (!videoId || !isGenerating) return;
    
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
            
            props.setEstimatedTimeRemaining(
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
            if (Math.floor(data.progress / 5) !== Math.floor((progress || 0) / 5)) {
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
  }, [videoId, videoUrl, isGenerating, logs, addLog, setError, 
      setIsGenerating, setPollingActive, setProgress, setStatusMessage, setVideoUrl]);
      
  return { pollingIntervalRef };
}; 