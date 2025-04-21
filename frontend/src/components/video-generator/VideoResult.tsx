'use client';

import React from 'react';
import { 
  Button, 
  Space, 
  Typography, 
  Card, 
  Row, 
  Col, 
  Divider, 
  Statistic,
  Badge
} from 'antd';
import { 
  DownloadOutlined, 
  ReloadOutlined, 
  CheckCircleOutlined,
  PlayCircleOutlined,
  ShareAltOutlined
} from '@ant-design/icons';
import VideoPlayer from '../video-player';

const { Text, Title } = Typography;

interface VideoResultProps {
  videoUrl: string;
  totalCost: number;
  setPrompt: (prompt: string) => void;
}

export const VideoResult: React.FC<VideoResultProps> = ({
  videoUrl,
  totalCost,
  setPrompt
}) => {
  return (
    <Card
      className="result-card"
      bordered={false}
      title={
        <Space align="center">
          <CheckCircleOutlined style={{ color: '#52c41a', fontSize: '24px' }} />
          <Title level={4} style={{ margin: 0 }}>Generation Complete</Title>
        </Space>
      }
      extra={
        <Statistic 
          title="Total Cost" 
          value={totalCost} 
          prefix="₹" 
          valueStyle={{ color: '#52c41a' }} 
        />
      }
      style={{ 
        borderRadius: '12px',
        boxShadow: '0 2px 8px rgba(0,0,0,0.05)'
      }}
    >
      <Row gutter={[24, 24]}>
        <Col span={24}>
          <div className="video-player-container" style={{ borderRadius: '8px', overflow: 'hidden' }}>
            <Badge.Ribbon text="AI Generated" color="#1890ff">
              <VideoPlayer videoUrl={videoUrl} />
            </Badge.Ribbon>
          </div>
        </Col>
        
        <Col span={24}>
          <Divider style={{ margin: '4px 0 16px 0' }} />
          
          <Row justify="space-between" align="middle">
            <Col>
              <Space>
                <Button
                  type="primary"
                  size="large"
                  icon={<DownloadOutlined />}
                  href={videoUrl}
                  target="_blank"
                  style={{ 
                    background: '#1890ff', 
                    borderRadius: '8px',
                    height: '42px'
                  }}
                >
                  Download Video
                </Button>
                
                <Button
                  size="large"
                  icon={<ShareAltOutlined />}
                  onClick={() => {
                    navigator.clipboard.writeText(videoUrl);
                  }}
                  style={{ borderRadius: '8px', height: '42px' }}
                >
                  Copy Link
                </Button>
              </Space>
            </Col>
            
            <Col>
              <Button
                type="default"
                size="large"
                icon={<ReloadOutlined />}
                onClick={() => setPrompt('')}
                style={{ 
                  borderRadius: '8px', 
                  height: '42px',
                  borderColor: '#1890ff',
                  color: '#1890ff'
                }}
              >
                Create New Video
              </Button>
            </Col>
          </Row>
        </Col>
      </Row>
    </Card>
  );
}; 