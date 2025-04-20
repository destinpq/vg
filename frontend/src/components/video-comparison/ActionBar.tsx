'use client';

import React from 'react';
import { Button, Space, Typography } from 'antd';
import { DownloadOutlined, CopyOutlined, ShareAltOutlined } from '@ant-design/icons';

const { Text } = Typography;

interface ActionBarProps {
  videoUrl: string;
  copiedUrl: boolean;
  metaData: Record<string, any>;
  copyVideoUrl: () => void;
  downloadVideo: () => void;
}

export const ActionBar: React.FC<ActionBarProps> = ({
  videoUrl,
  copiedUrl,
  metaData,
  copyVideoUrl,
  downloadVideo
}) => {
  return (
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
  );
}; 