'use client';

import React from 'react';
import { 
  Tabs, 
  Typography, 
  Card, 
  Row, 
  Col, 
  Badge, 
  Statistic, 
  Layout, 
  Menu, 
  Breadcrumb,
  Avatar,
  Tooltip
} from 'antd';
import { 
  RocketOutlined, 
  TeamOutlined, 
  PictureOutlined,
  HomeOutlined,
  AppstoreOutlined,
  UserOutlined,
  BellOutlined,
  SettingOutlined,
  DollarOutlined
} from '@ant-design/icons';
import VideoGenerator from '../components/video-generator';
import ConversationGenerator from '../components/conversation-generator';
import ImageToVideoGenerator from '../components/ImageToVideoGenerator';

const { Title, Paragraph, Text } = Typography;
const { Header, Content, Footer } = Layout;

export default function Home() {
  return (
    <Layout className="app-layout">
      <Header className="app-header" style={{ 
        background: 'white', 
        boxShadow: '0 2px 8px rgba(0,0,0,0.08)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        padding: '0 24px',
        position: 'sticky',
        top: 0,
        zIndex: 10
      }}>
        <div className="logo-area" style={{ display: 'flex', alignItems: 'center' }}>
          <RocketOutlined style={{ fontSize: 24, color: '#1890ff', marginRight: 12 }} />
          <Title level={3} style={{ margin: 0, color: '#1890ff' }}>Video Generator</Title>
        </div>
        
        <div className="header-actions" style={{ display: 'flex', alignItems: 'center', gap: 16 }}>
          <Badge count={5} size="small">
            <Tooltip title="Notifications">
              <BellOutlined style={{ fontSize: 18, color: '#595959' }} />
            </Tooltip>
          </Badge>
          
          <Badge dot>
            <Tooltip title="Settings">
              <SettingOutlined style={{ fontSize: 18, color: '#595959' }} />
            </Tooltip>
          </Badge>
          
          <Avatar 
            style={{ backgroundColor: '#1890ff', marginLeft: 8 }} 
            icon={<UserOutlined />} 
          />
        </div>
      </Header>
      
      <Content style={{ padding: '0 24px', marginTop: 24 }}>
        <div className="page-header" style={{ marginBottom: 24 }}>
          <Breadcrumb 
            items={[
              { title: <HomeOutlined />, href: '/' },
              { title: <AppstoreOutlined />, href: '/' },
              { title: 'Video Generation' }
            ]}
            style={{ marginBottom: 16 }}
          />
          
          <Row gutter={[24, 24]} align="middle">
            <Col xs={24} md={18}>
              <Title level={2} style={{ margin: 0, fontWeight: 600 }}>
                Create Amazing AI-Generated Videos
              </Title>
              <Paragraph style={{ marginTop: 8, fontSize: 16, color: '#595959' }}>
                Generate high-quality videos with our state-of-the-art AI models and customize every aspect of your creation.
              </Paragraph>
            </Col>
            
            <Col xs={24} md={6} style={{ textAlign: 'right' }}>
              <Card bordered={false} style={{ borderRadius: 8, background: '#f0f5ff' }}>
                <Statistic 
                  title={<Text strong>Cost Per API Call</Text>}
                  value={100}
                  prefix={<DollarOutlined />}
                  suffix="₹"
                  valueStyle={{ color: '#1890ff', fontWeight: 600 }}
                />
              </Card>
            </Col>
          </Row>
        </div>
        
        <Card 
          className="cost-info-card" 
          bordered={false}
          style={{ 
            background: 'linear-gradient(135deg, #e6f7ff 0%, #f0f5ff 100%)', 
            borderRadius: 12,
            boxShadow: '0 2px 14px rgba(24, 144, 255, 0.1)',
            marginBottom: 24
          }}
        >
          <Row align="middle" justify="space-between" gutter={[24, 16]}>
            <Col xs={24} lg={16}>
              <div style={{ display: 'flex', alignItems: 'center', gap: 16 }}>
                <div className="cost-icon-wrapper" style={{ 
                  width: 48, 
                  height: 48, 
                  borderRadius: '50%', 
                  background: 'rgba(24, 144, 255, 0.1)', 
                  display: 'flex', 
                  alignItems: 'center', 
                  justifyContent: 'center' 
                }}>
                  <DollarOutlined style={{ fontSize: 24, color: '#1890ff' }} />
                </div>
                <div>
                  <Title level={4} style={{ marginBottom: 4, color: '#1890ff' }}>
                    Server Cost Information
                  </Title>
                  <Paragraph style={{ margin: 0 }}>
                    Each server request costs <Badge color="#1890ff" count="₹100" style={{ backgroundColor: '#1890ff' }} /> - you can monitor usage in real-time with our enterprise cost tracking system.
                  </Paragraph>
                </div>
              </div>
            </Col>
            <Col xs={24} lg={8} style={{ textAlign: 'right' }}>
              <Statistic 
                title={<Text strong>Cost Per API Call</Text>}
                value={100} 
                prefix="₹" 
                valueStyle={{ color: '#1890ff', fontSize: 28 }} 
              />
              <Text type="secondary">Pricing effective from April 1, 2023</Text>
            </Col>
          </Row>
        </Card>
        
        <Tabs 
          defaultActiveKey="video" 
          type="card" 
          size="large"
          className="generation-tabs"
          tabBarStyle={{ 
            marginBottom: 24, 
            fontWeight: 500
          }}
          tabBarGutter={8}
          animated={{ inkBar: true, tabPane: true }}
        >
          <Tabs.TabPane 
            tab={
              <span className="tab-with-icon">
                <RocketOutlined />
                <span>Single Videos</span>
              </span>
            }
            key="video"
          >
            <Card 
              className="feature-card"
              bordered={false}
              style={{
                background: 'linear-gradient(135deg, #e6f7ff 0%, #f0f5ff 100%)',
                borderRadius: 12,
                marginBottom: 24,
                overflow: 'hidden',
                boxShadow: '0 4px 16px rgba(24, 144, 255, 0.1)'
              }}
            >
              <Row gutter={[24, 24]} align="middle">
                <Col xs={24} md={6} style={{ textAlign: 'center' }}>
                  <div style={{ 
                    width: 80, 
                    height: 80, 
                    margin: '0 auto',
                    borderRadius: '50%', 
                    background: 'rgba(24, 144, 255, 0.1)', 
                    display: 'flex', 
                    alignItems: 'center', 
                    justifyContent: 'center',
                    fontSize: 32,
                    color: '#1890ff'
                  }}>
                    ✨
                  </div>
                </Col>
                <Col xs={24} md={18}>
                  <Title level={3} style={{ color: '#1890ff', marginBottom: 8 }}>
                    AI Video Generation
                  </Title>
                  <Paragraph style={{ fontSize: 16, marginBottom: 8 }}>
                    Generate high-quality AI videos with detailed control over settings. Our proprietary algorithms produce cinema-quality visuals from simple text prompts.
                  </Paragraph>
                  <div className="feature-badges" style={{ display: 'flex', gap: 8, flexWrap: 'wrap' }}>
                    <Badge 
                      count="₹100 per request" 
                      style={{ 
                        backgroundColor: '#1890ff',
                        borderRadius: 16,
                        fontSize: 14,
                        padding: '0 12px',
                        height: 28,
                        lineHeight: '28px'
                      }} 
                    />
                    <Badge 
                      count="H100 GPU Powered" 
                      style={{ 
                        backgroundColor: '#52c41a',
                        borderRadius: 16,
                        fontSize: 14,
                        padding: '0 12px',
                        height: 28,
                        lineHeight: '28px'
                      }} 
                    />
                    <Badge 
                      count="Enterprise Ready" 
                      style={{ 
                        backgroundColor: '#722ed1',
                        borderRadius: 16,
                        fontSize: 14,
                        padding: '0 12px',
                        height: 28,
                        lineHeight: '28px'
                      }} 
                    />
                  </div>
                </Col>
              </Row>
            </Card>
            
            <VideoGenerator />
          </Tabs.TabPane>
          
          <Tabs.TabPane 
            tab={
              <span className="tab-with-icon">
                <TeamOutlined />
                <span>Conversation Videos</span>
              </span>
            }
            key="conversation"
          >
            <Card 
              className="feature-card"
              bordered={false}
              style={{
                background: 'linear-gradient(135deg, #f9f0ff 0%, #efdbff 100%)',
                borderRadius: 12,
                marginBottom: 24,
                overflow: 'hidden',
                boxShadow: '0 4px 16px rgba(114, 46, 209, 0.1)'
              }}
            >
              <Row gutter={[24, 24]} align="middle">
                <Col xs={24} md={6} style={{ textAlign: 'center' }}>
                  <div style={{ 
                    width: 80, 
                    height: 80, 
                    margin: '0 auto',
                    borderRadius: '50%', 
                    background: 'rgba(114, 46, 209, 0.1)', 
                    display: 'flex', 
                    alignItems: 'center', 
                    justifyContent: 'center',
                    fontSize: 32,
                    color: '#722ed1'
                  }}>
                    🎬
                  </div>
                </Col>
                <Col xs={24} md={18}>
                  <Title level={3} style={{ color: '#722ed1', marginBottom: 8 }}>
                    AI Conversation Generator
                  </Title>
                  <Paragraph style={{ fontSize: 16, marginBottom: 8 }}>
                    Generate videos of AI characters having realistic conversations on any topic. Perfect for educational content, presentations, and virtual conversations.
                  </Paragraph>
                  <div className="feature-badges" style={{ display: 'flex', gap: 8, flexWrap: 'wrap' }}>
                    <Badge 
                      count="₹100 per request" 
                      style={{ 
                        backgroundColor: '#722ed1',
                        borderRadius: 16,
                        fontSize: 14,
                        padding: '0 12px',
                        height: 28,
                        lineHeight: '28px'
                      }} 
                    />
                    <Badge 
                      count="Multi-character" 
                      style={{ 
                        backgroundColor: '#eb2f96',
                        borderRadius: 16,
                        fontSize: 14,
                        padding: '0 12px',
                        height: 28,
                        lineHeight: '28px'
                      }} 
                    />
                  </div>
                </Col>
              </Row>
            </Card>
            
            <ConversationGenerator />
          </Tabs.TabPane>
          
          <Tabs.TabPane 
            tab={
              <span className="tab-with-icon">
                <PictureOutlined />
                <span>Image to Video</span>
              </span>
            }
            key="i2v"
          >
            <Card 
              className="feature-card"
              bordered={false}
              style={{
                background: 'linear-gradient(135deg, #f6ffed 0%, #b7eb8f 100%)',
                borderRadius: 12,
                marginBottom: 24,
                overflow: 'hidden',
                boxShadow: '0 4px 16px rgba(82, 196, 26, 0.1)'
              }}
            >
              <Row gutter={[24, 24]} align="middle">
                <Col xs={24} md={6} style={{ textAlign: 'center' }}>
                  <div style={{ 
                    width: 80, 
                    height: 80, 
                    margin: '0 auto',
                    borderRadius: '50%', 
                    background: 'rgba(82, 196, 26, 0.1)', 
                    display: 'flex', 
                    alignItems: 'center', 
                    justifyContent: 'center',
                    fontSize: 32,
                    color: '#52c41a'
                  }}>
                    🖼️
                  </div>
                </Col>
                <Col xs={24} md={18}>
                  <Title level={3} style={{ color: '#52c41a', marginBottom: 8 }}>
                    Image to Video Animator
                  </Title>
                  <Paragraph style={{ fontSize: 16, marginBottom: 8 }}>
                    Transform still images into high-quality videos with consistent appearance. Bring your photos to life with fluid, natural motion that preserves the original image quality.
                  </Paragraph>
                  <div className="feature-badges" style={{ display: 'flex', gap: 8, flexWrap: 'wrap' }}>
                    <Badge 
                      count="₹100 per request" 
                      style={{ 
                        backgroundColor: '#52c41a',
                        borderRadius: 16,
                        fontSize: 14,
                        padding: '0 12px',
                        height: 28,
                        lineHeight: '28px'
                      }} 
                    />
                    <Badge 
                      count="High fidelity" 
                      style={{ 
                        backgroundColor: '#faad14',
                        borderRadius: 16,
                        fontSize: 14,
                        padding: '0 12px',
                        height: 28,
                        lineHeight: '28px'
                      }} 
                    />
                  </div>
                </Col>
              </Row>
            </Card>
            
            <ImageToVideoGenerator />
          </Tabs.TabPane>
        </Tabs>
      </Content>
      
      <Footer style={{ textAlign: 'center', background: '#f0f2f5', padding: '16px 24px' }}>
        <Row gutter={[16, 16]} justify="center">
          <Col>
            <Text type="secondary">Video Generator AI © 2023 Enterprise Edition v2.0</Text>
          </Col>
        </Row>
        <Row gutter={[16, 16]} justify="center" style={{ marginTop: 8 }}>
          <Col>
            <Text type="secondary">Powered by H100 GPUs</Text>
          </Col>
          <Col>
            <Text type="secondary">•</Text>
          </Col>
          <Col>
            <Text type="secondary">Built with Ant Design</Text>
          </Col>
          <Col>
            <Text type="secondary">•</Text>
          </Col>
          <Col>
            <Text type="secondary">Terms & Privacy</Text>
          </Col>
        </Row>
      </Footer>
    </Layout>
  );
} 