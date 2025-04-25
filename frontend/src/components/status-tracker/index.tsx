'use client';

import React from 'react';
import { Card, Space, Typography } from 'antd';
import { LoadingOutlined, CheckCircleOutlined, InfoCircleOutlined } from '@ant-design/icons';

import { LogEntry } from './types';
import { StatusHeader } from './StatusHeader';
import { ProgressDisplay } from './ProgressDisplay';
import { StageProgress } from './StageProgress';
import { PromptDisplay } from './PromptDisplay';
import { ParametersDisplay } from './ParametersDisplay';
import { LogTimeline } from './LogTimeline';

const { Title, Text } = Typography;

interface StatusTrackerProps {
  isGenerating: boolean;
  progress: number;
  statusMessage: string;
  logs: LogEntry[];
  prompt?: string;
  parameters?: Record<string, any>;
  estimatedTimeRemaining?: string;
  className?: string;
}

const StatusTracker: React.FC<StatusTrackerProps> = ({
  isGenerating,
  progress,
  statusMessage,
  logs = [],
  prompt,
  parameters,
  estimatedTimeRemaining,
  className = '',
}) => {
  return (
    <Card 
      className={`status-tracker ${className}`}
      bordered={false}
      style={{ 
        background: 'linear-gradient(to right, #f0f2f5, #f6f8fa)',
        borderRadius: '8px',
        boxShadow: '0 2px 12px rgba(0, 0, 0, 0.08)'
      }}
    >
      {/* Header with current status */}
      <StatusHeader 
        isGenerating={isGenerating} 
        progress={progress} 
        statusMessage={statusMessage}
        estimatedTimeRemaining={estimatedTimeRemaining}
      />

      {/* Overall Progress bar */}
      {(isGenerating || progress > 0) && (
        <ProgressDisplay progress={progress} isGenerating={isGenerating} />
      )}

      {/* Detailed stage progress */}
      {isGenerating && (
        <StageProgress progress={progress} />
      )}

      {/* Prompt display */}
      {prompt && (
        <PromptDisplay prompt={prompt} />
      )}

      {/* Parameters display */}
      {parameters && Object.keys(parameters).length > 0 && (
        <ParametersDisplay parameters={parameters} />
      )}

      {/* Timeline of events */}
      {logs.length > 0 && (
        <LogTimeline logs={logs} />
      )}
    </Card>
  );
};

export default StatusTracker; 