'use client';

import React from 'react';
import { FiDownload, FiCopy, FiInstagram, FiYoutube } from 'react-icons/fi';
import { 
  WhatsappShareButton, LinkedinShareButton, EmailShareButton,
  WhatsappIcon, LinkedinIcon, EmailIcon 
} from 'react-share';

interface VideoControlsProps {
  videoUrl: string;
  onCopyLink: () => void;
  copied: boolean;
}

export const VideoControls: React.FC<VideoControlsProps> = ({
  videoUrl,
  onCopyLink,
  copied
}) => {
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

  return (
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
            onClick={onCopyLink} 
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
  );
}; 