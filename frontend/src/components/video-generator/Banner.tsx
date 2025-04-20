'use client';

import React from 'react';
import { Alert, Typography, Space, Tag } from 'antd';

const { Title, Text } = Typography;

export const VideoGeneratorBanner: React.FC = () => {
  return (
    <Alert
      style={{ 
        marginBottom: 16, 
        backgroundColor: '#722ed1', 
        color: 'white', 
        padding: 12, 
        borderRadius: 8
      }}
      banner
      message={
        <div style={{ 
          display: 'flex', 
          justifyContent: 'space-between', 
          alignItems: 'center', 
          width: '100%' 
        }}>
          <Space>
            <span style={{ fontSize: 20, marginRight: 8 }}>🚀</span>
            <Title level={4} style={{ margin: 0, color: 'white' }}>
              REPLICATE API MODE
            </Title>
          </Space>
          <Tag style={{ 
            backgroundColor: '#9254de', 
            color: 'white', 
            fontSize: 12,
            padding: '2px 8px'
          }}>
            ₹100 per API call
          </Tag>
        </div>
      }
      description={
        <Text style={{ 
          fontSize: 14, 
          color: 'white', 
          marginTop: 4, 
          marginBottom: 0 
        }}>
          All video generation uses Replicate's H100 GPU (cost tracking enabled)
        </Text>
      }
    />
  );
}; 