'use client';

import React from 'react';
import { Typography } from 'antd';

const { Title, Text } = Typography;

export const Header: React.FC = () => {
  return (
    <div style={{ marginBottom: '16px' }}>
      <Title level={3} style={{ margin: 0 }}>Generate AI Conversation Videos</Title>
      <Text type="secondary">
        Create videos of two AI characters having a conversation about any topic with subtitles and lip sync.
      </Text>
    </div>
  );
}; 