'use client';

import React, { useState } from 'react';
import { 
  Input, 
  Button, 
  Select, 
  Slider, 
  Space, 
  Typography, 
  Switch, 
  Form, 
  Row, 
  Col, 
  Card, 
  Divider,
  Tooltip,
  Tag,
  Popover,
  Progress,
  Segmented,
  Radio
} from 'antd';
import { 
  VideoCameraOutlined, 
  SettingOutlined, 
  ClockCircleOutlined,
  StarOutlined, 
  UserOutlined, 
  ExperimentOutlined,
  QuestionCircleOutlined,
  ThunderboltOutlined,
  BulbOutlined,
  ToolOutlined,
  SlidersFilled
} from '@ant-design/icons';

const { Text, Title, Paragraph } = Typography;
const { Option } = Select;

interface VideoFormProps {
  prompt: string;
  setPrompt: (prompt: string) => void;
  duration: number;
  setDuration: (duration: number) => void;
  showAdvanced: boolean;
  setShowAdvanced: (show: boolean) => void;
  quality: string;
  setQuality: (quality: string) => void;
  useRealistic: boolean;
  setUseRealistic: (use: boolean) => void;
  humanFocus: boolean;
  setHumanFocus: (use: boolean) => void;
  isGenerating: boolean;
  handleSubmit: (e: React.FormEvent) => Promise<void>;
}

export const VideoForm: React.FC<VideoFormProps> = ({
  prompt,
  setPrompt,
  duration,
  setDuration,
  showAdvanced,
  setShowAdvanced,
  quality,
  setQuality,
  useRealistic,
  setUseRealistic,
  humanFocus,
  setHumanFocus,
  isGenerating,
  handleSubmit
}) => {
  const [promptSuggestions] = useState([
    "A serene mountain lake at sunrise with mist rising from the water",
    "A bustling futuristic city with flying cars and holographic billboards",
    "A cozy cafe interior with rain falling outside the windows",
    "An underwater coral reef teeming with colorful fish and sea life"
  ]);
  
  const [promptStrength, setPromptStrength] = useState(85);
  
  // Function to calculate prompt quality based on length and complexity
  const calculatePromptQuality = (text: string): number => {
    if (!text) return 0;
    // Simple heuristic based on length and keyword diversity
    const baseScore = Math.min(100, Math.max(0, text.length / 5));
    const hasDescription = /descri(b|pt)/i.test(text) ? 10 : 0;
    const hasColors = /(blue|red|green|yellow|purple|orange|turquoise|golden|silver)/i.test(text) ? 10 : 0;
    const hasAdjectives = /(beautiful|stunning|amazing|gorgeous|detailed|intricate|realistic|vibrant)/i.test(text) ? 10 : 0;
    const hasScene = /(scene|setting|environment|background|foreground)/i.test(text) ? 10 : 0;
    
    return Math.min(100, baseScore + hasDescription + hasColors + hasAdjectives + hasScene);
  };
  
  const promptQuality = calculatePromptQuality(prompt);
  
  // Get quality score color
  const getQualityColor = (score: number) => {
    if (score >= 80) return '#52c41a';
    if (score >= 50) return '#faad14';
    return '#f5222d';
  };
  
  const getQualityLabel = (score: number) => {
    if (score >= 80) return 'Excellent';
    if (score >= 50) return 'Good';
    if (score >= 30) return 'Basic';
    return 'Poor';
  };
  
  return (
    <Form layout="vertical" onFinish={handleSubmit} className="video-form">
      <Form.Item 
        label={
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
            <Space>
              <BulbOutlined style={{ color: '#1890ff' }} />
              <Title level={5} style={{ margin: 0 }}>Enter your video description:</Title>
            </Space>
            <Space size="small">
              <Text type="secondary">Prompt Quality:</Text>
              <Progress 
                type="circle" 
                percent={promptQuality} 
                width={24} 
                strokeColor={getQualityColor(promptQuality)}
                format={() => ''}
              />
              <Text style={{ color: getQualityColor(promptQuality) }}>
                {getQualityLabel(promptQuality)}
              </Text>
              <Tooltip title="Include details about scene, colors, lighting, and style for best results">
                <QuestionCircleOutlined style={{ color: '#1890ff' }} />
              </Tooltip>
            </Space>
          </div>
        }
        required
        tooltip="Be descriptive and specific about what you want to see in the video"
      >
        <Input.TextArea
          rows={5}
          placeholder="Describe the video you want to generate in detail... (e.g., A serene lake at sunset with mountains in the background, reflections in the water, cinematic lighting)"
          value={prompt}
          onChange={(e) => setPrompt(e.target.value)}
          disabled={isGenerating}
          className="text-area-input"
          showCount
          maxLength={500}
          autoSize={{ minRows: 4, maxRows: 8 }}
          style={{ 
            borderRadius: '8px',
            boxShadow: 'inset 0 2px 4px rgba(0, 0, 0, 0.05)'
          }}
        />
        
        <div style={{ marginTop: 8 }}>
          <Text type="secondary">Suggestions:</Text>
          <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap', marginTop: 4 }}>
            {promptSuggestions.map((suggestion, index) => (
              <Tag 
                key={index}
                color="blue"
                style={{ cursor: 'pointer', padding: '4px 8px' }}
                onClick={() => setPrompt(suggestion)}
              >
                {suggestion.length > 40 ? suggestion.substring(0, 40) + '...' : suggestion}
              </Tag>
            ))}
          </div>
        </div>
      </Form.Item>
      
      <Row gutter={[16, 16]} align="middle" justify="space-between">
        <Col xs={24} md={12}>
          <Card
            size="small"
            title={
              <Space>
                <ThunderboltOutlined style={{ color: '#1890ff' }} />
                <span>Generation Strength</span>
              </Space>
            }
            bordered={false}
            style={{ 
              background: '#f5f5f5', 
              borderRadius: 8,
              boxShadow: 'inset 0 2px 4px rgba(0, 0, 0, 0.05)'
            }}
          >
            <Slider
              min={50}
              max={100}
              value={promptStrength}
              onChange={setPromptStrength}
              marks={{
                50: 'Subtle',
                75: 'Balanced',
                100: 'Strong'
              }}
              disabled={isGenerating}
              tooltipVisible
            />
          </Card>
        </Col>
        
        <Col xs={24} md={12}>
          <Form.Item 
            label={<Space><ClockCircleOutlined /> <Text strong>Video Duration</Text></Space>}
            tooltip="Longer videos will take more time to generate"
          >
            <Row gutter={[8, 0]} align="middle">
              <Col span={16}>
                <Slider
                  min={2}
                  max={10}
                  value={duration}
                  onChange={setDuration}
                  disabled={isGenerating}
                  marks={{ 2: '2s', 5: '5s', 10: '10s' }}
                  tooltip={{ formatter: (value) => `${value}s` }}
                />
              </Col>
              <Col span={8} style={{ textAlign: 'center' }}>
                <Tag 
                  style={{ 
                    padding: '4px 8px', 
                    fontSize: 14,
                    borderRadius: 16
                  }}
                  color="blue"
                >
                  {duration} seconds
                </Tag>
              </Col>
            </Row>
          </Form.Item>
        </Col>
      </Row>
      
      <Form.Item>
        <Button
          type="primary"
          htmlType="submit"
          size="large"
          icon={<VideoCameraOutlined />}
          loading={isGenerating}
          disabled={!prompt.trim() || isGenerating}
          style={{ 
            background: 'linear-gradient(90deg, #1890ff, #096dd9)', 
            height: '48px', 
            borderRadius: '8px', 
            fontWeight: 600,
            width: '100%',
            border: 'none',
            boxShadow: '0 4px 12px rgba(24, 144, 255, 0.4)'
          }}
        >
          Generate Professional Video
        </Button>
      </Form.Item>
      
      <Divider>
        <Button 
          type="link" 
          onClick={() => setShowAdvanced(!showAdvanced)}
          icon={<SettingOutlined />}
          disabled={isGenerating}
          style={{ display: 'flex', alignItems: 'center' }}
        >
          {showAdvanced ? 'Hide Advanced Settings' : 'Show Advanced Settings'}
        </Button>
      </Divider>
      
      {showAdvanced && (
        <Card 
          bordered={false} 
          className="advanced-settings-card"
          title={
            <Space>
              <SlidersFilled style={{ color: '#1890ff' }} />
              <span>Advanced Generation Options</span>
            </Space>
          }
          style={{ 
            background: 'linear-gradient(to right, #f9f9ff, #f0f5ff)',
            borderRadius: '12px',
            overflow: 'hidden',
            boxShadow: '0 4px 12px rgba(0, 0, 0, 0.05)'
          }}
        >
          <Row gutter={[32, 24]}>
            <Col xs={24} md={8}>
              <Form.Item
                label={
                  <Space align="center">
                    <StarOutlined style={{ color: '#faad14' }} />
                    <Text strong>Output Quality</Text>
                  </Space>
                }
                tooltip="Higher quality takes longer but produces better results"
              >
                <Radio.Group 
                  value={quality} 
                  onChange={(e) => setQuality(e.target.value)} 
                  disabled={isGenerating}
                  buttonStyle="solid"
                  style={{ width: '100%' }}
                >
                  <Space direction="vertical" style={{ width: '100%' }}>
                    <Radio.Button value="low" style={{ width: '100%', textAlign: 'left', height: 'auto', padding: '8px 12px' }}>
                      <Space direction="vertical" style={{ width: '100%' }}>
                        <Text strong>Draft Quality</Text>
                        <Text type="secondary" style={{ fontSize: 12 }}>Faster generation (15-20s)</Text>
                      </Space>
                    </Radio.Button>
                    <Radio.Button value="medium" style={{ width: '100%', textAlign: 'left', height: 'auto', padding: '8px 12px' }}>
                      <Space direction="vertical" style={{ width: '100%' }}>
                        <Text strong>Standard Quality</Text>
                        <Text type="secondary" style={{ fontSize: 12 }}>Balanced option (30-40s)</Text>
                      </Space>
                    </Radio.Button>
                    <Radio.Button value="high" style={{ width: '100%', textAlign: 'left', height: 'auto', padding: '8px 12px' }}>
                      <Space direction="vertical" style={{ width: '100%' }}>
                        <Text strong>Premium Quality</Text>
                        <Text type="secondary" style={{ fontSize: 12 }}>Best results (50-60s)</Text>
                      </Space>
                    </Radio.Button>
                  </Space>
                </Radio.Group>
              </Form.Item>
            </Col>
            
            <Col xs={24} md={8}>
              <Form.Item
                label={
                  <Space align="center">
                    <ExperimentOutlined style={{ color: '#722ed1' }} />
                    <Text strong>Visual Style</Text>
                  </Space>
                }
                tooltip="Choose between realistic or abstract artistic style"
              >
                <Card bordered={false} bodyStyle={{ padding: '16px' }}>
                  <div style={{ textAlign: 'center', marginBottom: 16 }}>
                    <Segmented
                      value={useRealistic ? 'realistic' : 'abstract'}
                      onChange={(value) => setUseRealistic(value === 'realistic')}
                      disabled={isGenerating}
                      options={[
                        {
                          label: (
                            <div style={{ padding: '4px 8px' }}>
                              <div>🌄</div>
                              <div>Realistic</div>
                            </div>
                          ),
                          value: 'realistic',
                        },
                        {
                          label: (
                            <div style={{ padding: '4px 8px' }}>
                              <div>🎨</div>
                              <div>Abstract</div>
                            </div>
                          ),
                          value: 'abstract',
                        },
                      ]}
                    />
                  </div>
                  
                  <Paragraph style={{ margin: 0, fontSize: 13 }}>
                    {useRealistic ? 
                      'Photorealistic style with natural lighting and textures' : 
                      'Creative artistic style with vibrant colors and unique visual elements'}
                  </Paragraph>
                </Card>
              </Form.Item>
            </Col>
            
            <Col xs={24} md={8}>
              <Form.Item
                label={
                  <Space align="center">
                    <UserOutlined style={{ color: '#eb2f96' }} />
                    <Text strong>Human Optimization</Text>
                  </Space>
                }
                tooltip="Enable specialized models optimized for human subjects"
              >
                <Card 
                  bordered={false} 
                  bodyStyle={{ padding: 0 }}
                  style={{ borderRadius: 8 }}
                >
                  <div 
                    style={{
                      display: 'flex',
                      alignItems: 'center',
                      padding: '16px',
                      gap: 16
                    }}
                  >
                    <Switch
                      checked={humanFocus}
                      onChange={setHumanFocus}
                      disabled={isGenerating}
                      checkedChildren="On"
                      unCheckedChildren="Off"
                    />
                    <div>
                      <Text strong>{humanFocus ? 'Enabled' : 'Disabled'}</Text>
                      <Paragraph style={{ margin: 0, fontSize: 13 }}>
                        {humanFocus ? 
                          'Specialized optimization for human facial features and body proportions' : 
                          'Standard generation without specific human optimizations'}
                      </Paragraph>
                    </div>
                  </div>
                </Card>
              </Form.Item>
            </Col>
          </Row>
          
          <Popover 
            content={
              <div style={{ maxWidth: 300 }}>
                <Title level={5}>Using Advanced Settings</Title>
                <Paragraph>
                  These settings allow fine-tuning of the AI generation process. For best results:
                </Paragraph>
                <ul style={{ paddingLeft: 16 }}>
                  <li>Use Premium Quality for important videos</li>
                  <li>Choose Realistic for photographic scenes</li>
                  <li>Enable Human Optimization when people are the focus</li>
                </ul>
              </div>
            } 
            title="Advanced Settings Help"
            trigger="click"
          >
            <Button 
              type="link" 
              icon={<QuestionCircleOutlined />}
              style={{ float: 'right', marginTop: 8 }}
            >
              Settings Help
            </Button>
          </Popover>
        </Card>
      )}
    </Form>
  );
}; 