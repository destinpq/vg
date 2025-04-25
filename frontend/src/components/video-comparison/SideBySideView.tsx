'use client';

import React from 'react';
import { Typography, Image } from 'antd';
import { ExpandOutlined } from '@ant-design/icons';
import VideoPlayer from '../video-player';

const { Title } = Typography;

interface SideBySideViewProps {
  imageUrl: string;
  videoUrl: string;
}

export const SideBySideView: React.FC<SideBySideViewProps> = ({ imageUrl, videoUrl }) => {
  return (
    <div 
      className="comparison-container" 
      style={{ 
        display: 'grid', 
        gridTemplateColumns: '1fr 1fr',
        gap: '16px',
        marginBottom: '16px'
      }}
    >
      <div className="original-image">
        <Title level={5} style={{ marginTop: 0, marginBottom: '8px' }}>Original Image</Title>
        <div style={{ borderRadius: '8px', overflow: 'hidden' }}>
          <Image 
            src={imageUrl} 
            alt="Original image"
            width="100%"
            style={{ objectFit: 'cover' }}
            preview={{ 
              mask: <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                <ExpandOutlined style={{ fontSize: '24px' }} /> View Fullsize
              </div>
            }}
          />
        </div>
      </div>
      
      <div className="generated-video">
        <Title level={5} style={{ marginTop: 0, marginBottom: '8px' }}>Generated Video</Title>
        <div style={{ borderRadius: '8px', overflow: 'hidden', height: '100%' }}>
          <VideoPlayer 
            videoUrl={videoUrl} 
            autoPlay={true}
            loop={true}
            controls={true}
          />
        </div>
      </div>
    </div>
  );
}; 