'use client';

import React, { useState, useEffect, useRef } from 'react';
import { 
  Input, Button, Card, Typography, Switch, Tag, 
  Tooltip, Popover, Divider, Spin, Space 
} from 'antd';
import { 
  RocketOutlined, BulbOutlined, EditOutlined, 
  LoadingOutlined, CheckOutlined, SyncOutlined,
  DownOutlined, FireOutlined
} from '@ant-design/icons';

const { TextArea } = Input;
const { Text, Title, Paragraph } = Typography;

interface PromptEnhancerProps {
  initialPrompt: string;
  onPromptChange: (prompt: string) => void;
  enhancePrompt?: (prompt: string) => Promise<{enhanced: string, changes?: string[]}>;
  enhanceEnabled?: boolean;
  onEnableChange?: (enabled: boolean) => void;
  suggestions?: string[];
  loading?: boolean;
  placeholder?: string;
  className?: string;
}

const PromptEnhancer: React.FC<PromptEnhancerProps> = ({
  initialPrompt,
  onPromptChange,
  enhancePrompt,
  enhanceEnabled = true,
  onEnableChange,
  suggestions = [],
  loading = false,
  placeholder = "Describe what you want to generate...",
  className = '',
}) => {
  const [prompt, setPrompt] = useState(initialPrompt);
  const [enhancedPrompt, setEnhancedPrompt] = useState('');
  const [changes, setChanges] = useState<string[]>([]);
  const [isEnhancing, setIsEnhancing] = useState(false);
  const [showEnhanced, setShowEnhanced] = useState(false);
  const [diffView, setDiffView] = useState(false);
  const textAreaRef = useRef<any>(null);

  // Handle external prompt changes
  useEffect(() => {
    setPrompt(initialPrompt);
  }, [initialPrompt]);

  // Handle enhancement
  const handleEnhance = async () => {
    if (!enhancePrompt || !prompt.trim()) return;
    
    setIsEnhancing(true);
    try {
      const result = await enhancePrompt(prompt);
      setEnhancedPrompt(result.enhanced);
      setChanges(result.changes || []);
      setShowEnhanced(true);
    } catch (error) {
      console.error('Error enhancing prompt:', error);
    } finally {
      setIsEnhancing(false);
    }
  };

  // Apply enhanced prompt
  const applyEnhanced = () => {
    if (enhancedPrompt) {
      setPrompt(enhancedPrompt);
      onPromptChange(enhancedPrompt);
      setShowEnhanced(false);
    }
  };

  // Handle prompt input change
  const handlePromptChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    const newPrompt = e.target.value;
    setPrompt(newPrompt);
    onPromptChange(newPrompt);
    // Reset enhanced view when user edits
    if (showEnhanced) {
      setShowEnhanced(false);
    }
  };

  // Add suggestion to prompt
  const addSuggestion = (suggestion: string) => {
    const newPrompt = prompt ? `${prompt}, ${suggestion}` : suggestion;
    setPrompt(newPrompt);
    onPromptChange(newPrompt);
    if (textAreaRef.current) {
      textAreaRef.current.focus();
    }
  };

  // Toggle AI enhancement
  const toggleEnhance = (checked: boolean) => {
    if (onEnableChange) {
      onEnableChange(checked);
    }
  };

  return (
    <div className={`prompt-enhancer ${className}`}>
      <Card
        className="prompt-card"
        bordered={false}
        style={{ 
          borderRadius: '10px',
          boxShadow: '0 4px 12px rgba(0, 0, 0, 0.08)'
        }}
      >
        <div className="prompt-header" style={{ marginBottom: '12px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <Title level={5} style={{ margin: 0 }}>
            <Space>
              <RocketOutlined style={{ color: '#1890ff' }} />
              Your Prompt
            </Space>
          </Title>
          
          {enhancePrompt && (
            <Tooltip title="Enable AI enhancement for better results">
              <div className="ai-enhance-toggle">
                <Text style={{ marginRight: '8px' }}>AI Enhancement</Text>
                <Switch 
                  checked={enhanceEnabled}
                  onChange={toggleEnhance}
                  checkedChildren={<CheckOutlined />}
                  disabled={loading}
                />
              </div>
            </Tooltip>
          )}
        </div>
        
        {/* Main prompt textarea */}
        <div className="prompt-input-container" style={{ position: 'relative' }}>
          <TextArea
            ref={textAreaRef}
            value={prompt}
            onChange={handlePromptChange}
            placeholder={placeholder}
            autoSize={{ minRows: 3, maxRows: 6 }}
            disabled={loading || isEnhancing}
            className="prompt-textarea"
            style={{ 
              resize: 'none',
              fontSize: '15px',
              borderRadius: '8px',
              padding: '12px',
              backgroundColor: loading ? 'rgba(0,0,0,0.02)' : 'white'
            }}
          />
          {loading && (
            <div style={{ position: 'absolute', right: '12px', top: '12px' }}>
              <LoadingOutlined style={{ fontSize: '16px', color: '#1890ff' }} />
            </div>
          )}
        </div>
        
        {/* Suggestions */}
        {suggestions.length > 0 && (
          <div className="prompt-suggestions" style={{ marginTop: '10px' }}>
            <Text type="secondary" style={{ display: 'block', marginBottom: '6px', fontSize: '13px' }}>
              <BulbOutlined style={{ marginRight: '4px' }} /> Suggestions:
            </Text>
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px' }}>
              {suggestions.map((suggestion, index) => (
                <Tag
                  key={index}
                  color="blue"
                  style={{ cursor: 'pointer', borderRadius: '4px' }}
                  onClick={() => addSuggestion(suggestion)}
                >
                  {suggestion}
                </Tag>
              ))}
            </div>
          </div>
        )}
        
        {/* Enhanced prompt view */}
        {enhanceEnabled && enhancePrompt && (
          <div className="enhance-actions" style={{ marginTop: '12px', display: 'flex', justifyContent: 'flex-end' }}>
            {!showEnhanced ? (
              <Button
                type="primary"
                icon={<RocketOutlined />}
                onClick={handleEnhance}
                loading={isEnhancing}
                disabled={!prompt.trim() || loading}
                style={{ borderRadius: '6px' }}
              >
                Enhance Prompt
              </Button>
            ) : (
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
            )}
          </div>
        )}
      </Card>
    </div>
  );
};

export default PromptEnhancer; 