'use client';

import React from 'react';
import { Space, Typography, Tag } from 'antd';
import { LoadingOutlined, CheckCircleOutlined, InfoCircleOutlined } from '@ant-design/icons';

const { Text } = Typography;

interface StatusHeaderProps {
  isGenerating: boolean;
  progress: number;
  statusMessage: string;
  estimatedTimeRemaining?: string;
}

export const StatusHeader: React.FC<StatusHeaderProps> = ({
  isGenerating,
  progress,
  statusMessage,
  estimatedTimeRemaining
}) => {
  return (
    <div className="status-header mb-4">
      <Space align="center" style={{ width: '100%', justifyContent: 'space-between' }}>
        <div>
          <Text strong style={{ fontSize: '16px', display: 'flex', alignItems: 'center', marginBottom: '4px' }}>
            {isGenerating ? (
              <>
                <LoadingOutlined style={{ marginRight: 8 }} />
                Generation in progress
              </>
            ) : progress === 100 ? (
              <>
                <CheckCircleOutlined style={{ marginRight: 8, color: '#52c41a' }} />
                Generation complete
              </>
            ) : (
              <>
                <InfoCircleOutlined style={{ marginRight: 8 }} />
                Status
              </>
            )}
          </Text>
          <Text type="secondary">{statusMessage}</Text>
        </div>
        
        {isGenerating && estimatedTimeRemaining && (
          <Tag color="blue">
            Est. time remaining: {estimatedTimeRemaining}
          </Tag>
        )}
      </Space>
    </div>
  );
}; 