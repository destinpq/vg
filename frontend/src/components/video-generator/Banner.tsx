'use client';

import React from 'react';
import { Alert, Typography, Space, Tag, Row, Col, Statistic, Badge, Card } from 'antd';
import { 
  RocketOutlined, 
  ThunderboltOutlined, 
  ApiOutlined,
  GlobalOutlined,
  CheckCircleOutlined,
  BarChartOutlined
} from '@ant-design/icons';

const { Text, Title, Paragraph } = Typography;

export const VideoGeneratorBanner: React.FC = () => {
  return (
    <Card
      className="enterprise-banner"
      bordered={false}
      bodyStyle={{ padding: 0 }}
      style={{
        borderRadius: '12px 12px 0 0',
        overflow: 'hidden',
        marginBottom: '20px',
        boxShadow: '0 4px 16px rgba(24, 144, 255, 0.15)'
      }}
    >
      <div className="banner-gradient" style={{
        background: 'linear-gradient(135deg, #1890ff 0%, #096dd9 100%)',
        padding: '16px 24px',
        position: 'relative',
        overflow: 'hidden'
      }}>
        {/* Animated background elements */}
        <div className="animated-circles" style={{ position: 'absolute', top: 0, left: 0, right: 0, bottom: 0, overflow: 'hidden', zIndex: 1 }}>
          {[...Array(5)].map((_, i) => (
            <div 
              key={i} 
              style={{
                position: 'absolute',
                width: `${40 + i * 15}px`,
                height: `${40 + i * 15}px`,
                borderRadius: '50%',
                background: 'rgba(255, 255, 255, 0.1)',
                top: `${Math.random() * 100}%`,
                left: `${Math.random() * 100}%`,
                transform: 'translate(-50%, -50%)',
                animation: `float ${5 + i}s ease-in-out infinite alternate`
              }}
            />
          ))}
        </div>
        
        <Row align="middle" justify="space-between" style={{ position: 'relative', zIndex: 2 }}>
          <Col xs={24} md={18}>
            <Space align="center" size="large">
              <div className="gpu-icon" style={{
                width: 48,
                height: 48,
                borderRadius: '8px',
                background: 'rgba(255, 255, 255, 0.2)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                boxShadow: '0 4px 12px rgba(0, 0, 0, 0.1)'
              }}>
                <ThunderboltOutlined style={{ color: 'white', fontSize: 24 }} />
              </div>
              
              <div>
                <div style={{ display: 'flex', alignItems: 'center', marginBottom: 4 }}>
                  <Title level={4} style={{ margin: 0, color: 'white' }}>
                    ENTERPRISE GPU CLUSTER
                  </Title>
                  <Tag 
                    color="green" 
                    icon={<CheckCircleOutlined />}
                    style={{ 
                      marginLeft: 12, 
                      borderRadius: 16,
                      padding: '0 8px',
                      fontSize: 12,
                      height: 22,
                      lineHeight: '22px'
                    }}
                  >
                    ONLINE
                  </Tag>
                </div>
                <Paragraph style={{ color: 'rgba(255, 255, 255, 0.85)', margin: 0 }}>
                  Powered by H100 GPUs with enterprise-grade infrastructure and real-time cost tracking
                </Paragraph>
              </div>
            </Space>
          </Col>
          
          <Col xs={24} md={6} style={{ textAlign: 'right' }}>
            <Space size="large">
              <Statistic 
                title={<Text style={{ color: 'rgba(255, 255, 255, 0.85)', fontSize: 12 }}>API Credits</Text>}
                value={950}
                suffix="/ 1000"
                valueStyle={{ color: 'white', fontSize: 16, fontWeight: 600 }}
              />
              <Badge 
                count="H100 GPU"
                style={{ 
                  backgroundColor: '#52c41a',
                  borderRadius: 16,
                  padding: '0 12px',
                  fontSize: 12,
                  boxShadow: '0 2px 8px rgba(0, 0, 0, 0.15)'
                }}
              />
            </Space>
          </Col>
        </Row>
      </div>
      
      <div className="banner-stats" style={{ padding: '12px', background: '#f0f9ff' }}>
        <Row justify="space-around" align="middle">
          <Col span={8} style={{ textAlign: 'center' }}>
            <Space>
              <ApiOutlined style={{ color: '#1890ff' }} />
              <Text strong>Cost tracked</Text>
            </Space>
          </Col>
          <Col span={8} style={{ textAlign: 'center' }}>
            <Space>
              <BarChartOutlined style={{ color: '#1890ff' }} />
              <Text strong>High performance</Text>
            </Space>
          </Col>
          <Col span={8} style={{ textAlign: 'center' }}>
            <Space>
              <GlobalOutlined style={{ color: '#1890ff' }} />
              <Text strong>Global availability</Text>
            </Space>
          </Col>
        </Row>
      </div>
      
      <style jsx global>{`
        @keyframes float {
          0% { transform: translate(-50%, -50%) scale(1); opacity: 0.5; }
          100% { transform: translate(-50%, -50%) scale(1.2); opacity: 0.7; }
        }
      `}</style>
    </Card>
  );
}; 