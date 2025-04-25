'use client';

import React from 'react';
import { Typography, Tag } from 'antd';

const { Text } = Typography;

interface ParametersDisplayProps {
  parameters: Record<string, any>;
}

export const ParametersDisplay: React.FC<ParametersDisplayProps> = ({ parameters }) => {
  return (
    <div className="parameters-display mb-4">
      <Text strong style={{ display: 'block', marginBottom: '4px' }}>
        Parameters:
      </Text>
      <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px' }}>
        {Object.entries(parameters).map(([key, value]) => (
          <Tag key={key} color="orange">
            {key}: {typeof value === 'object' ? JSON.stringify(value) : value.toString()}
          </Tag>
        ))}
      </div>
    </div>
  );
}; 