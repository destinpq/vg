'use client';

import React from 'react';
import { Timeline } from 'antd';
import { CheckCircleOutlined, CloseCircleOutlined, LoadingOutlined, 
         InfoCircleOutlined, ExperimentOutlined, RocketOutlined } from '@ant-design/icons';
import { LogEntry } from './types';

interface LogTimelineProps {
  logs: LogEntry[];
}

export const LogTimeline: React.FC<LogTimelineProps> = ({ logs }) => {
  // Format timestamp
  const formatTime = (timestamp: string) => {
    try {
      const date = new Date(timestamp);
      return date.toLocaleTimeString();
    } catch {
      return timestamp;
    }
  };

  // Get icon based on log type
  const getIcon = (type: string) => {
    switch (type) {
      case 'success':
        return <CheckCircleOutlined style={{ color: '#52c41a' }} />;
      case 'error':
        return <CloseCircleOutlined style={{ color: '#f5222d' }} />;
      case 'loading':
        return <LoadingOutlined style={{ color: '#1890ff' }} />;
      case 'prompt':
        return <ExperimentOutlined style={{ color: '#722ed1' }} />;
      case 'parameter':
        return <RocketOutlined style={{ color: '#faad14' }} />;
      case 'info':
      default:
        return <InfoCircleOutlined style={{ color: '#1890ff' }} />;
    }
  };

  return (
    <div className="log-timeline" style={{ maxHeight: '240px', overflowY: 'auto', paddingRight: '10px' }}>
      <Timeline>
        {logs.map((log, index) => (
          <Timeline.Item 
            key={index} 
            dot={getIcon(log.type)}
          >
            <div className="log-entry">
              <span style={{ fontWeight: 'bold' }}>{formatTime(log.timestamp)}</span>
              <span style={{ marginLeft: '8px' }}>{log.message}</span>
              
              {log.data && (
                <div className="log-data" style={{ marginTop: '4px', marginLeft: '16px' }}>
                  {typeof log.data === 'string' ? (
                    <span style={{ fontSize: '12px', color: '#8c8c8c' }}>{log.data}</span>
                  ) : (
                    <pre style={{ 
                      fontSize: '12px', 
                      background: '#f5f5f5', 
                      padding: '4px 8px', 
                      borderRadius: '4px',
                      margin: '4px 0 0 0',
                      maxHeight: '80px',
                      overflowY: 'auto'
                    }}>
                      {JSON.stringify(log.data, null, 2)}
                    </pre>
                  )}
                </div>
              )}
            </div>
          </Timeline.Item>
        ))}
      </Timeline>
    </div>
  );
}; 