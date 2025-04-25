'use client';

import React from 'react';
import { Typography } from 'antd';

const { Text, Paragraph } = Typography;

interface PromptDisplayProps {
  prompt: string;
}

export const PromptDisplay: React.FC<PromptDisplayProps> = ({ prompt }) => {
  return (
    <div className="prompt-display mb-4 p-3" style={{ 
      background: 'rgba(113, 46, 209, 0.05)', 
      borderRadius: '6px', 
      border: '1px solid rgba(113, 46, 209, 0.1)' 
    }}>
      <Text strong style={{ display: 'block', marginBottom: '4px', color: '#722ed1' }}>
        Prompt:
      </Text>
      <Paragraph copyable style={{ margin: 0 }}>
        {prompt}
      </Paragraph>
    </div>
  );
}; 