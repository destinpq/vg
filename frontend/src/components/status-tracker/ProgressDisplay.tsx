'use client';

import React from 'react';
import { Progress } from 'antd';

interface ProgressDisplayProps {
  progress: number;
  isGenerating: boolean;
}

export const ProgressDisplay: React.FC<ProgressDisplayProps> = ({
  progress,
  isGenerating
}) => {
  return (
    <Progress 
      percent={Math.round(progress)} 
      status={isGenerating ? "active" : progress === 100 ? "success" : "normal"}
      strokeColor={{
        '0%': '#108ee9',
        '100%': '#87d068',
      }}
      className="mb-4"
    />
  );
}; 