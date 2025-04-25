'use client';

import React from 'react';
import { Typography } from 'antd';
import { UserOutlined, RobotOutlined } from '@ant-design/icons';

const { Title, Text } = Typography;

export const EmptyState: React.FC = () => {
  return (
    <div style={{ 
      padding: '32px', 
      backgroundColor: '#f9f9f9', 
      borderRadius: '8px', 
      border: '1px solid #e9e9e9',
      textAlign: 'center'
    }}>
      <div style={{ display: 'flex', justifyContent: 'center' }}>
        <UserOutlined style={{ fontSize: '36px', color: '#1890ff', marginRight: '12px' }} />
        <RobotOutlined style={{ fontSize: '36px', color: '#722ed1' }} />
      </div>
      <Title level={4} style={{ marginTop: '16px' }}>Your conversation video will appear here</Title>
      <Text type="secondary">
        Enter a topic, adjust the settings to your preference, and click "Generate Conversation" to create an AI-driven conversation video.
      </Text>
    </div>
  );
}; 