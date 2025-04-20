'use client';

import React, { useState, useRef, useEffect } from 'react';
import ReactPlayer from 'react-player/lazy';
import { 
  WhatsappShareButton, LinkedinShareButton, EmailShareButton,
  WhatsappIcon, LinkedinIcon, EmailIcon 
} from 'react-share';
import { FiDownload, FiCopy, FiInstagram, FiYoutube } from 'react-icons/fi';

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
  const [actualUrl, setActualUrl] = useState(videoUrl);
  
  // Reset copied state after 2 seconds
  useEffect(() => {
    if (copied) {
      const timeout = setTimeout(() => setCopied(false), 2000);
      return () => clearTimeout(timeout);
    }
  }, [copied]);

  useEffect(() => {
    // Don't replace port 5555, as that's our actual backend server
    let newUrl = videoUrl;
    
    // Support both old and new URL formats
    if (videoUrl.includes('localhost:8000')) {
      newUrl = videoUrl.replace('localhost:8000', 'localhost:5001');
    } else if (videoUrl.includes('localhost:8080')) {
      newUrl = videoUrl.replace('localhost:8080', 'localhost:5001');
    } else if (videoUrl.includes('localhost:50080')) {
      newUrl = videoUrl.replace('localhost:50080', 'localhost:5001');
    } else if (videoUrl.includes('localhost:54321')) {
      newUrl = videoUrl.replace('localhost:54321', 'localhost:5001');
    } else if (videoUrl.includes('localhost:63456')) {
      newUrl = videoUrl.replace('localhost:63456', 'localhost:5001');
    } else if (videoUrl.includes('localhost:5555')) {
      newUrl = videoUrl.replace('localhost:5555', 'localhost:5001');
    }
    
    // Make sure the URL has the /output/ prefix if it's missing
    if ((newUrl.includes('/localhost:5001/') || newUrl.includes('/localhost:5555/')) && !newUrl.includes('/output/')) {
      newUrl = newUrl.replace(/\/localhost:(5001|5555)\//, '/localhost:$1/output/');
    }
    
    console.log('Original video URL:', videoUrl);
    console.log('Actual video URL:', newUrl);
    
    setActualUrl(newUrl);
  }, [videoUrl]);

  const handleCopyLink = () => {
    navigator.clipboard.writeText(videoUrl);
    setCopied(true);
  };
  
  const handleInstagramShare = () => {
    // Mobile deep link for Instagram
    const instagramUrl = `instagram://library?AssetPath=${encodeURIComponent(videoUrl)}`;
    // Try to open the deep link, fallback to browser
    window.open(instagramUrl, '_blank') || window.open('https://www.instagram.com', '_blank');
  };
  
  const handleYouTubeShare = () => {
    // Since direct YouTube upload isn't possible via JavaScript,
    // we'll open YouTube upload page in a new tab
    window.open('https://studio.youtube.com/channel/upload', '_blank');
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
      
      <div className="video-actions">
        <div className="share-buttons">
          <h4>Share:</h4>
          <div className="share-icons">
            <button 
              onClick={handleInstagramShare} 
              className="social-button instagram-button"
              aria-label="Share to Instagram"
            >
              <FiInstagram size={22} />
              <span className="social-button-text">Instagram</span>
            </button>
            
            <button 
              onClick={handleYouTubeShare} 
              className="social-button youtube-button"
              aria-label="Share to YouTube"
            >
              <FiYoutube size={22} />
              <span className="social-button-text">YouTube</span>
            </button>
            
            <WhatsappShareButton url={videoUrl} title="Check out this AI-generated video!">
              <WhatsappIcon size={40} round />
            </WhatsappShareButton>
            
            <LinkedinShareButton url={videoUrl} title="AI-Generated Video">
              <LinkedinIcon size={40} round />
            </LinkedinShareButton>
            
            <EmailShareButton url={videoUrl} subject="Check out this AI-generated video!" body="I created this amazing video with AI:">
              <EmailIcon size={40} round />
            </EmailShareButton>
            
            <button 
              onClick={handleCopyLink} 
              className={`copy-button ${copied ? 'copied' : ''}`}
              aria-label="Copy video link"
            >
              <FiCopy size={20} />
              <span className="tooltip-text">{copied ? 'Copied!' : 'Copy link'}</span>
            </button>
          </div>
        </div>
        
        <a 
          href={videoUrl} 
          download 
          className="download-button"
          target="_blank"
          rel="noopener noreferrer"
        >
          <FiDownload size={20} />
          <span>Download MP4</span>
        </a>
      </div>
    </div>
  );
};

export default VideoPlayer; 