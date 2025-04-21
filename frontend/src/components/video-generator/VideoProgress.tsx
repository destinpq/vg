'use client';

import React from 'react';
import { Progress, Typography, Card, Space, Row, Col, Tag, Statistic } from 'antd';
import { 
  LoadingOutlined, 
  RocketOutlined, 
  ApiOutlined,
  DollarOutlined
} from '@ant-design/icons';

const { Text, Title } = Typography;

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
  // Determine status color based on progress
  const getStatusColor = () => {
    if (progress < 30) return '#1890ff'; // Blue for starting
    if (progress < 70) return '#52c41a'; // Green for mid-progress
    return '#722ed1'; // Purple for near completion
  };

  return (
    <Card 
      className="progress-card" 
      bordered={false}
      style={{ 
        background: 'linear-gradient(to right, #f0f8ff, #f9f0ff)',
        borderRadius: '12px',
        padding: '12px'
      }}
    >
      <Row gutter={[16, 16]} align="middle">
        <Col span={24}>
          <Space align="center" style={{ marginBottom: '12px' }}>
            <LoadingOutlined spin style={{ fontSize: '24px', color: getStatusColor() }} />
            <Title level={4} style={{ margin: 0, color: getStatusColor() }}>
              Generating Your Video
            </Title>
          </Space>
        </Col>
        
        <Col span={24}>
          <Progress 
            percent={progress} 
            status="active"
            strokeColor={{
              '0%': '#1890ff',
              '100%': '#722ed1',
            }}
            strokeWidth={10}
            style={{ marginBottom: '16px' }}
          />
        </Col>
        
        <Col xs={24} md={16}>
          <Card 
            size="small" 
            bordered={false}
            style={{ background: 'rgba(255, 255, 255, 0.7)' }}
          >
            <Space direction="vertical" size="small" style={{ width: '100%' }}>
              <Text strong>Status: {statusMessage}</Text>
              {diffusionStep && (
                <Text type="secondary">
                  Processing Step: {diffusionStep}
                </Text>
              )}
            </Space>
          </Card>
        </Col>
        
        <Col xs={24} md={8}>
          <Row gutter={[16, 0]}>
            <Col span={12}>
              <Statistic 
                title={<Space><ApiOutlined /> API Calls</Space>}
                value={apiCallCount}
                valueStyle={{ color: '#1890ff' }}
              />
            </Col>
            <Col span={12}>
              <Statistic 
                title={<Space><DollarOutlined /> Cost</Space>}
                value={totalCost}
                prefix="₹"
                precision={0}
                valueStyle={{ color: '#52c41a' }}
              />
            </Col>
          </Row>
        </Col>
      </Row>
    </Card>
  );
}; 