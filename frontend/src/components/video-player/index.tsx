'use client';

import React, { useState, useRef, useEffect } from 'react';
import ReactPlayer from 'react-player/lazy';
import { VideoControls } from './VideoControls';
import { useVideoUrl } from './hooks/useVideoUrl';

interface VideoPlayerProps {
  videoUrl: string;
  autoPlay?: boolean;
  loop?: boolean;
  controls?: boolean;
  muted?: boolean;
  className?: string;
}

const VideoPlayer: React.FC<VideoPlayerProps> = ({
  videoUrl,
  autoPlay = true,
  loop = true,
  controls = true,
  muted = true,
  className = '',
}) => {
  const [copied, setCopied] = useState(false);
  const [playerReady, setPlayerReady] = useState(false);
  const playerRef = useRef<ReactPlayer | null>(null);
  const [error, setError] = useState<string | null>(null);
  
  // Use our custom hook to handle URL formatting
  const { actualUrl } = useVideoUrl(videoUrl);
  
  // Reset copied state after 2 seconds
  useEffect(() => {
    if (copied) {
      const timeout = setTimeout(() => setCopied(false), 2000);
      return () => clearTimeout(timeout);
    }
  }, [copied]);

  const handleCopyLink = () => {
    navigator.clipboard.writeText(videoUrl);
    setCopied(true);
  };

  const handleError = () => {
    setError('Video cannot be played. Please try again later.');
  };

  return (
    <div className={`video-player-container ${className}`}>
      {error ? (
        <div className="video-error">{error}</div>
      ) : (
        <div className="video-player-wrapper">
          <ReactPlayer
            ref={playerRef}
            url={actualUrl}
            width="100%"
            height="100%"
            controls={controls}
            playing={autoPlay}
            onReady={() => setPlayerReady(true)}
            onError={handleError}
            className="react-player"
          />
        </div>
      )}
      
      <VideoControls 
        videoUrl={videoUrl} 
        onCopyLink={handleCopyLink} 
        copied={copied} 
      />
    </div>
  );
};

export default VideoPlayer; 