'use client';

import React from 'react';
import { Button, Space, Typography } from 'antd';
import VideoPlayer from '../video-player';

const { Text } = Typography;

interface VideoResultProps {
  videoUrl: string;
  totalCost: number;
  setPrompt: (prompt: string) => void;
}

export const VideoResult: React.FC<VideoResultProps> = ({
  videoUrl,
  totalCost,
  setPrompt
}) => {
  return (
    <div className="mt-6">
      <div className="flex justify-between items-center mb-2">
        <Text strong>Generated Video:</Text>
        <Text type="success">Final Cost: ₹{totalCost}</Text>
      </div>
      <VideoPlayer videoUrl={videoUrl} />
      <div className="mt-4 flex justify-end">
        <Space>
          <Button type="primary" href={videoUrl} target="_blank">
            Download
          </Button>
          <Button onClick={() => setPrompt('')}>New Video</Button>
        </Space>
      </div>
    </div>
  );
}; 