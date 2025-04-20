'use client';

import React, { useState } from 'react';
import { Card, Typography, Divider, Space, Button, Tooltip } from 'antd';
import { SwapOutlined, ExpandOutlined, CompressOutlined } from '@ant-design/icons';
import { VideoComparisonProps } from './types';
import { SideBySideView } from './SideBySideView';
import { TabView } from './TabView';
import { ActionBar } from './ActionBar';

const { Title } = Typography;

const VideoComparison: React.FC<VideoComparisonProps> = ({
  title = 'Generated Result',
  imageUrl,
  videoUrl,
  metaData = {},
  showImageComparison = true,
  className = '',
}) => {
  const [activeTab, setActiveTab] = useState('video');
  const [fullscreen, setFullscreen] = useState(false);
  const [layout, setLayout] = useState<'side-by-side' | 'stacked'>(
    showImageComparison ? 'side-by-side' : 'stacked'
  );
  const [copiedUrl, setCopiedUrl] = useState(false);

  const handleTabChange = (key: string) => {
    setActiveTab(key);
  };

  const toggleFullscreen = () => {
    setFullscreen(!fullscreen);
  };

  const toggleLayout = () => {
    setLayout(layout === 'side-by-side' ? 'stacked' : 'side-by-side');
  };

  const copyVideoUrl = () => {
    navigator.clipboard.writeText(videoUrl);
    setCopiedUrl(true);
    setTimeout(() => setCopiedUrl(false), 2000);
  };

  const downloadVideo = () => {
    // Create a link and trigger download
    const link = document.createElement('a');
    link.href = videoUrl;
    link.download = 'generated-video.mp4';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  return (
    <div className={`video-comparison ${className} ${fullscreen ? 'fullscreen' : ''}`}>
      <Card
        className="result-card"
        bordered={false}
        bodyStyle={{ padding: fullscreen ? '24px' : '16px' }}
        style={{ 
          borderRadius: '10px',
          boxShadow: '0 4px 16px rgba(0, 0, 0, 0.1)',
          position: fullscreen ? 'fixed' : 'relative',
          top: fullscreen ? 0 : 'auto',
          left: fullscreen ? 0 : 'auto',
          right: fullscreen ? 0 : 'auto',
          bottom: fullscreen ? 0 : 'auto',
          zIndex: fullscreen ? 1000 : 1,
          margin: fullscreen ? 0 : undefined,
          height: fullscreen ? '100vh' : 'auto',
          width: fullscreen ? '100vw' : '100%',
          backgroundColor: fullscreen ? '#fff' : undefined,
          transition: 'all 0.3s ease'
        }}
      >
        <div className="result-header" style={{ 
          display: 'flex', 
          justifyContent: 'space-between', 
          alignItems: 'center', 
          marginBottom: '16px'
        }}>
          <Title level={4} style={{ margin: 0 }}>{title}</Title>
          
          <Space>
            {showImageComparison && imageUrl && (
              <Tooltip title={layout === 'side-by-side' ? 'Stack view' : 'Side-by-side view'}>
                <Button 
                  icon={<SwapOutlined />} 
                  onClick={toggleLayout}
                  shape="circle"
                />
              </Tooltip>
            )}
            <Tooltip title={fullscreen ? 'Exit fullscreen' : 'Fullscreen'}>
              <Button 
                icon={fullscreen ? <CompressOutlined /> : <ExpandOutlined />} 
                onClick={toggleFullscreen}
                shape="circle"
              />
            </Tooltip>
          </Space>
        </div>

        {showImageComparison && imageUrl && layout === 'side-by-side' ? (
          <SideBySideView imageUrl={imageUrl} videoUrl={videoUrl} />
        ) : (
          <TabView 
            activeTab={activeTab}
            handleTabChange={handleTabChange}
            imageUrl={imageUrl}
            videoUrl={videoUrl}
            showImageComparison={showImageComparison}
          />
        )}

        <Divider style={{ margin: '16px 0' }} />
        
        <ActionBar 
          videoUrl={videoUrl}
          copiedUrl={copiedUrl}
          metaData={metaData}
          copyVideoUrl={copyVideoUrl}
          downloadVideo={downloadVideo}
        />
      </Card>
    </div>
  );
};

export default VideoComparison; 