'use client';

import React from 'react';
import { Button, Divider, Space, Typography, Tag } from 'antd';
import { FireOutlined, SyncOutlined, EditOutlined, CheckOutlined } from '@ant-design/icons';

const { Text, Paragraph } = Typography;

interface EnhancedPromptViewProps {
  enhancedPrompt: string;
  changes: string[];
  diffView: boolean;
  setDiffView: (show: boolean) => void;
  setShowEnhanced: (show: boolean) => void;
  applyEnhanced: () => void;
}

export const EnhancedPromptView: React.FC<EnhancedPromptViewProps> = ({
  enhancedPrompt,
  changes,
  diffView,
  setDiffView,
  setShowEnhanced,
  applyEnhanced,
}) => {
  return (
    <div style={{ width: '100%' }}>
      <Divider style={{ margin: '12px 0' }}>
        <Space>
          <FireOutlined style={{ color: '#ff4d4f' }} />
          <Text strong>Enhanced Prompt</Text>
          <Button 
            type="text" 
            size="small" 
            icon={<SyncOutlined />} 
            onClick={() => setDiffView(!diffView)}
          >
            {diffView ? 'Hide Changes' : 'Show Changes'}
          </Button>
        </Space>
      </Divider>
      
      <div 
        className="enhanced-display"
        style={{ 
          padding: '12px', 
          borderRadius: '8px', 
          backgroundColor: 'rgba(24, 144, 255, 0.05)', 
          border: '1px solid rgba(24, 144, 255, 0.1)',
          marginBottom: '12px'
        }}
      >
        {diffView && changes.length > 0 ? (
          <div>
            {changes.map((change, idx) => (
              <Text key={idx} style={{ display: 'block', marginBottom: '4px' }}>
                <Tag color="green" style={{ marginRight: '8px' }}>+</Tag>
                {change}
              </Text>
            ))}
          </div>
        ) : (
          <Paragraph copyable style={{ margin: 0 }}>{enhancedPrompt}</Paragraph>
        )}
      </div>
      
      <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '8px' }}>
        <Button 
          icon={<EditOutlined />} 
          onClick={() => setShowEnhanced(false)}
        >
          Edit Original
        </Button>
        <Button 
          type="primary" 
          icon={<CheckOutlined />} 
          onClick={applyEnhanced}
        >
          Use Enhanced
        </Button>
      </div>
    </div>
  );
}; 