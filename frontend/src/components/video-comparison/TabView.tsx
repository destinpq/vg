'use client';

import React from 'react';
import { Tabs, Image } from 'antd';
import { ExpandOutlined } from '@ant-design/icons';
import VideoPlayer from '../video-player';

const { TabPane } = Tabs;

interface TabViewProps {
  activeTab: string;
  handleTabChange: (key: string) => void;
  imageUrl?: string;
  videoUrl: string;
  showImageComparison: boolean;
}

export const TabView: React.FC<TabViewProps> = ({
  activeTab,
  handleTabChange,
  imageUrl,
  videoUrl,
  showImageComparison
}) => {
  return (
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
  );
}; 