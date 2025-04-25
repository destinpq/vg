'use client';

import React from 'react';
import { Tag, Typography } from 'antd';
import { BulbOutlined } from '@ant-design/icons';

const { Text } = Typography;

interface SuggestionTagsProps {
  suggestions: string[];
  addSuggestion: (suggestion: string) => void;
}

export const SuggestionTags: React.FC<SuggestionTagsProps> = ({
  suggestions,
  addSuggestion,
}) => {
  if (suggestions.length === 0) {
    return null;
  }

  return (
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
  );
}; 