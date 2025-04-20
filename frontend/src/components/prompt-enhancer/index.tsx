'use client';

import React, { useState, useEffect, useRef } from 'react';
import { Input, Button, Card, Typography, Switch, Tooltip, Space } from 'antd';
import { RocketOutlined, CheckOutlined, LoadingOutlined } from '@ant-design/icons';
import { PromptEnhancerProps } from './types';
import { SuggestionTags } from './SuggestionTags';
import { EnhancedPromptView } from './EnhancedPromptView';

const { TextArea } = Input;
const { Text, Title } = Typography;

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
        <div className="prompt-header" style={{ 
          marginBottom: '12px', 
          display: 'flex', 
          justifyContent: 'space-between', 
          alignItems: 'center' 
        }}>
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
        <SuggestionTags 
          suggestions={suggestions} 
          addSuggestion={addSuggestion} 
        />
        
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
              <EnhancedPromptView
                enhancedPrompt={enhancedPrompt}
                changes={changes}
                diffView={diffView}
                setDiffView={setDiffView}
                setShowEnhanced={setShowEnhanced}
                applyEnhanced={applyEnhanced}
              />
            )}
          </div>
        )}
      </Card>
    </div>
  );
};

export default PromptEnhancer; 