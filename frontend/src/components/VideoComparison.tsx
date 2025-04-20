'use client';

import React, { useState } from 'react';
import { Card, Typography, Tabs, Image, Button, Space, Divider, Tooltip } from 'antd';
import { 
  SwapOutlined, ExpandOutlined, CompressOutlined, 
  DownloadOutlined, CopyOutlined, ShareAltOutlined 
} from '@ant-design/icons';
import VideoPlayer from './VideoPlayer';

const { Text, Title } = Typography;
const { TabPane } = Tabs;

interface VideoComparisonProps {
  title?: string;
  imageUrl?: string;
  videoUrl: string;
  metaData?: Record<string, any>;
  showImageComparison?: boolean;
  className?: string;
}

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
        ) : (
          <div className="content-container">
            {showImageComparison && imageUrl ? (
              <Tabs 
                activeKey={activeTab} 
                onChange={handleTabChange}
                className="result-tabs"
                type="card"
              >
                <TabPane tab="Generated Video" key="video">
                  <div style={{ borderRadius: '8px', overflow: 'hidden' }}>
                    <VideoPlayer 
                      videoUrl={videoUrl} 
                      autoPlay={true}
                      loop={true}
                      controls={true}
                    />
                  </div>
                </TabPane>
                <TabPane tab="Original Image" key="image">
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
                </TabPane>
              </Tabs>
            ) : (
              <div style={{ borderRadius: '8px', overflow: 'hidden' }}>
                <VideoPlayer 
                  videoUrl={videoUrl} 
                  autoPlay={true}
                  loop={true}
                  controls={true}
                />
              </div>
            )}
          </div>
        )}

        <Divider style={{ margin: '16px 0' }} />
        
        {/* Actions bar */}
        <div className="result-actions" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <Space>
            <Button 
              icon={<DownloadOutlined />} 
              onClick={downloadVideo}
              type="primary"
            >
              Download
            </Button>
            <Button 
              icon={<CopyOutlined />} 
              onClick={copyVideoUrl}
            >
              {copiedUrl ? 'Copied!' : 'Copy URL'}
            </Button>
            <Button 
              icon={<ShareAltOutlined />} 
              onClick={() => {
                if (navigator.share) {
                  navigator.share({
                    title: 'Check out my AI-generated video',
                    url: videoUrl
                  });
                } else {
                  copyVideoUrl();
                }
              }}
            >
              Share
            </Button>
          </Space>
          
          {Object.keys(metaData).length > 0 && (
            <div className="meta-data">
              {Object.entries(metaData).map(([key, value]) => (
                <Text key={key} type="secondary" style={{ marginRight: '12px' }}>
                  <span style={{ fontWeight: 'bold' }}>{key}:</span> {value}
                </Text>
              ))}
            </div>
          )}
        </div>
      </Card>
    </div>
  );
};

export default VideoComparison; 