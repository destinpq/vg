'use client';

import React from 'react';
import { Progress, Typography } from 'antd';

const { Text } = Typography;

interface VideoProgressProps {
  totalCost: number;
  apiCallCount: number;
  progress: number;
  statusMessage: string;
  diffusionStep: string;
}

export const VideoProgress: React.FC<VideoProgressProps> = ({
  totalCost,
  apiCallCount,
  progress,
  statusMessage,
  diffusionStep
}) => {
  return (
    <div className="mt-6">
      <div className="flex justify-between items-center mb-2">
        <Text strong>Generating your video...</Text>
        <div className="flex items-center">
          <span className="text-purple-600 font-medium mr-2">
            Cost: ₹{totalCost}
          </span>
          <span className="text-gray-500 text-sm">
            ({apiCallCount} API calls)
          </span>
        </div>
      </div>
      
      <Progress percent={progress} status="active" />
      
      <div className="mt-2 text-sm text-gray-500 flex justify-between">
        <span>{statusMessage}</span>
        {diffusionStep && <span>Step: {diffusionStep}</span>}
      </div>
    </div>
  );
}; 