'use client';

import React from 'react';
import { Card, Row, Col, Select, Typography, Divider, Button } from 'antd';
import { MessageOutlined } from '@ant-design/icons';
import PromptEnhancer from '../../prompt-enhancer';
import { SubtitleStyle } from '../types';

const { Option } = Select;
const { Text } = Typography;

interface ConversationFormProps {
  topic: string;
  handleTopicChange: (topic: string) => void;
  durationMinutes: number;
  setDurationMinutes: (duration: number) => void;
  segmentDuration: number;
  setSegmentDuration: (duration: number) => void;
  videoWidth: number;
  setVideoWidth: (width: number) => void;
  videoHeight: number;
  setVideoHeight: (height: number) => void;
  subtitleStyle: SubtitleStyle;
  setSubtitleStyle: (style: SubtitleStyle) => void;
  enhanceTopic: boolean;
  setEnhanceTopic: (enhance: boolean) => void;
  enhanceTopicWithAI: (topic: string) => Promise<any>;
  isGenerating: boolean;
  handleSubmit: (e: React.FormEvent) => Promise<void>;
  suggestions: string[];
}

export const ConversationForm: React.FC<ConversationFormProps> = ({
  topic,
  handleTopicChange,
  durationMinutes,
  setDurationMinutes,
  segmentDuration,
  setSegmentDuration,
  videoWidth,
  setVideoWidth,
  videoHeight,
  setVideoHeight,
  subtitleStyle,
  setSubtitleStyle,
  enhanceTopic,
  setEnhanceTopic,
  enhanceTopicWithAI,
  isGenerating,
  handleSubmit,
  suggestions
}) => {
  return (
    <>
      {/* Topic with PromptEnhancer */}
      <Card title="Step 1: Conversation Topic" style={{ boxShadow: '0 2px 8px rgba(0, 0, 0, 0.1)' }}>
        <PromptEnhancer
          initialPrompt={topic}
          onPromptChange={handleTopicChange}
          enhancePrompt={enhanceTopicWithAI}
          enhanceEnabled={enhanceTopic}
          onEnableChange={setEnhanceTopic}
          suggestions={suggestions}
          loading={isGenerating}
          placeholder="Enter a topic for the AI conversation (e.g., 'Climate change and its impact on society')"
        />
      </Card>
      
      {/* Duration & Settings */}
      <Card title="Step 2: Duration & Settings" style={{ marginTop: 16, boxShadow: '0 2px 8px rgba(0, 0, 0, 0.1)' }}>
        <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
          <div>
            <Text strong>Conversation Duration:</Text>
            <Row gutter={16} align="middle" style={{ marginTop: 8 }}>
              <Col span={16}>
                <Select
                  style={{ width: '100%' }}
                  value={durationMinutes}
                  onChange={setDurationMinutes}
                  disabled={isGenerating}
                >
                  <Option value={0.5}>30 Seconds</Option>
                  <Option value={1}>1 Minute</Option>
                  <Option value={2}>2 Minutes</Option>
                  <Option value={5}>5 Minutes</Option>
                  <Option value={10}>10 Minutes</Option>
                </Select>
              </Col>
              <Col span={8}>
                <Text type="secondary" style={{ fontSize: 12 }}>
                  Longer = more time to generate
                </Text>
              </Col>
            </Row>
          </div>
          
          <div>
            <Text strong>Segment Duration:</Text>
            <Row gutter={16} align="middle" style={{ marginTop: 8 }}>
              <Col span={16}>
                <Select
                  style={{ width: '100%' }}
                  value={segmentDuration}
                  onChange={setSegmentDuration}
                  disabled={isGenerating}
                >
                  <Option value={3}>3 Seconds</Option>
                  <Option value={5}>5 Seconds</Option>
                  <Option value={8}>8 Seconds</Option>
                  <Option value={10}>10 Seconds</Option>
                </Select>
              </Col>
              <Col span={8}>
                <Text type="secondary" style={{ fontSize: 12 }}>
                  How long each person speaks
                </Text>
              </Col>
            </Row>
          </div>
          
          <Divider style={{ margin: '12px 0' }} />
          
          <div>
            <Text strong>Video Size:</Text>
            <Row gutter={16} style={{ marginTop: 8 }}>
              <Col span={12}>
                <Select
                  style={{ width: '100%' }}
                  value={videoWidth}
                  onChange={setVideoWidth}
                  disabled={isGenerating}
                >
                  <Option value={1280}>1280px (Width)</Option>
                  <Option value={1920}>1920px (Width)</Option>
                </Select>
              </Col>
              <Col span={12}>
                <Select
                  style={{ width: '100%' }}
                  value={videoHeight}
                  onChange={setVideoHeight}
                  disabled={isGenerating}
                >
                  <Option value={720}>720px (Height)</Option>
                  <Option value={1080}>1080px (Height)</Option>
                </Select>
              </Col>
            </Row>
          </div>
          
          <div>
            <Text strong>Subtitle Style:</Text>
            <Row gutter={16} style={{ marginTop: 8 }}>
              <Col span={8}>
                <Text style={{ fontSize: 12 }}>Font Size:</Text>
                <Select
                  style={{ width: '100%' }}
                  value={subtitleStyle.font_size}
                  onChange={(value) => setSubtitleStyle({...subtitleStyle, font_size: value})}
                  disabled={isGenerating}
                >
                  <Option value={30}>Small</Option>
                  <Option value={40}>Medium</Option>
                  <Option value={50}>Large</Option>
                </Select>
              </Col>
              <Col span={8}>
                <Text style={{ fontSize: 12 }}>Font Color:</Text>
                <Select
                  style={{ width: '100%' }}
                  value={subtitleStyle.font_color}
                  onChange={(value) => setSubtitleStyle({...subtitleStyle, font_color: value})}
                  disabled={isGenerating}
                >
                  <Option value="white">White</Option>
                  <Option value="yellow">Yellow</Option>
                  <Option value="black">Black</Option>
                </Select>
              </Col>
              <Col span={8}>
                <Text style={{ fontSize: 12 }}>Background:</Text>
                <Select
                  style={{ width: '100%' }}
                  value={subtitleStyle.bg_alpha}
                  onChange={(value) => setSubtitleStyle({...subtitleStyle, bg_alpha: value})}
                  disabled={isGenerating}
                >
                  <Option value={0}>None</Option>
                  <Option value={0.3}>Light</Option>
                  <Option value={0.5}>Medium</Option>
                  <Option value={0.8}>Dark</Option>
                </Select>
              </Col>
            </Row>
          </div>
        </div>
      </Card>
      
      {/* Generate Button */}
      <div style={{ display: 'flex', justifyContent: 'center', marginTop: 24 }}>
        <Button
          type="primary"
          size="large"
          icon={<MessageOutlined />}
          onClick={handleSubmit}
          disabled={isGenerating || !topic.trim()}
          loading={isGenerating}
          style={{ 
            borderRadius: '8px', 
            height: '50px', 
            fontSize: '16px',
            padding: '0 32px'
          }}
        >
          {isGenerating ? 'Generating...' : 'Generate Conversation'}
        </Button>
      </div>
    </>
  );
}; 