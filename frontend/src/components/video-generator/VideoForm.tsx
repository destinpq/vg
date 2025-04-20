'use client';

import React from 'react';
import { Input, Button, Select, Slider, Space, Typography, Switch } from 'antd';
import { VideoCameraOutlined } from '@ant-design/icons';

const { Text } = Typography;
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
  return (
    <div className="mt-6">
      <Text strong>Enter your video description:</Text>
      <Input.TextArea
        rows={4}
        placeholder="Describe the video you want to generate in detail..."
        value={prompt}
        onChange={(e) => setPrompt(e.target.value)}
        disabled={isGenerating}
        className="mt-2"
      />
      
      <div className="flex justify-between items-center mt-4">
        <Button
          type="primary"
          size="large"
          icon={<VideoCameraOutlined />}
          onClick={handleSubmit}
          loading={isGenerating}
          disabled={!prompt.trim() || isGenerating}
          className="bg-purple-600 hover:bg-purple-700"
        >
          Generate Video
        </Button>
        
        <Space>
          <Text>Duration: {duration}s</Text>
          <Slider
            min={2}
            max={10}
            value={duration}
            onChange={setDuration}
            disabled={isGenerating}
            style={{ width: 120 }}
          />
          
          <Button
            type="link"
            onClick={() => setShowAdvanced(!showAdvanced)}
            disabled={isGenerating}
          >
            {showAdvanced ? 'Hide Advanced' : 'Show Advanced'}
          </Button>
        </Space>
      </div>
      
      {showAdvanced && (
        <div className="grid grid-cols-2 gap-4 mt-4 p-4 bg-gray-50 rounded-lg">
          <div>
            <Text>Quality:</Text>
            <Select
              style={{ width: '100%' }}
              value={quality}
              onChange={setQuality}
              disabled={isGenerating}
            >
              <Option value="low">Low (Faster)</Option>
              <Option value="medium">Medium</Option>
              <Option value="high">High (Better Quality)</Option>
            </Select>
          </div>
          
          <div>
            <Text>Style Type:</Text>
            <div className="flex items-center mt-2">
              <Switch
                checked={useRealistic}
                onChange={setUseRealistic}
                disabled={isGenerating}
              />
              <Text className="ml-2">{useRealistic ? 'Realistic' : 'Abstract'}</Text>
            </div>
          </div>
          
          <div>
            <Text>Human Focus:</Text>
            <div className="flex items-center mt-2">
              <Switch
                checked={humanFocus}
                onChange={setHumanFocus}
                disabled={isGenerating}
              />
              <Text className="ml-2">{humanFocus ? 'Enabled' : 'Disabled'}</Text>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}; 