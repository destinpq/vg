'use client';

import React, { useMemo } from 'react';
import { Progress, Timeline, Spin, Typography, Tag, Card, Space, Steps } from 'antd';
import { 
  LoadingOutlined, CheckCircleOutlined, CloseCircleOutlined, 
  InfoCircleOutlined, RocketOutlined, ExperimentOutlined,
  VideoCameraOutlined, FileImageOutlined, CodeOutlined,
  SettingOutlined, CloudUploadOutlined, CloudDownloadOutlined
} from '@ant-design/icons';

const { Text, Title, Paragraph } = Typography;
const { Step } = Steps;

interface LogEntry {
  timestamp: string;
  message: string;
  type: 'info' | 'success' | 'error' | 'loading' | 'prompt' | 'parameter';
  data?: any;
}

interface StatusTrackerProps {
  isGenerating: boolean;
  progress: number;
  statusMessage: string;
  logs: LogEntry[];
  prompt?: string;
  parameters?: Record<string, any>;
  estimatedTimeRemaining?: string;
  className?: string;
}

// Video generation stages with their percentage thresholds
const generationStages = [
  { title: 'Initializing', icon: <SettingOutlined />, threshold: 15 },
  { title: 'Loading Model', icon: <CloudDownloadOutlined />, threshold: 20 },
  { title: 'Processing Prompt', icon: <CodeOutlined />, threshold: 25 },
  { title: 'Generating Latents', icon: <RocketOutlined />, threshold: 30 },
  { title: 'Diffusion Steps', icon: <ExperimentOutlined />, threshold: 90 },
  { title: 'Rendering Frames', icon: <FileImageOutlined />, threshold: 95 },
  { title: 'Finalizing Video', icon: <VideoCameraOutlined />, threshold: 100 }
];

const StatusTracker: React.FC<StatusTrackerProps> = ({
  isGenerating,
  progress,
  statusMessage,
  logs = [],
  prompt,
  parameters,
  estimatedTimeRemaining,
  className = '',
}) => {
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

  // Calculate the current stage based on progress
  const currentStageIndex = useMemo(() => {
    if (progress >= 100) return generationStages.length - 1;
    for (let i = 0; i < generationStages.length; i++) {
      if (progress < generationStages[i].threshold) {
        return i;
      }
    }
    return 0;
  }, [progress]);

  // Calculate percentage within current stage
  const stageProgress = useMemo(() => {
    if (currentStageIndex === 0) return progress / generationStages[0].threshold * 100;
    
    const prevThreshold = generationStages[currentStageIndex - 1].threshold;
    const currentThreshold = generationStages[currentStageIndex].threshold;
    const range = currentThreshold - prevThreshold;
    
    return ((progress - prevThreshold) / range) * 100;
  }, [progress, currentStageIndex]);

  return (
    <Card 
      className={`status-tracker ${className}`}
      bordered={false}
      style={{ 
        background: 'linear-gradient(to right, #f0f2f5, #f6f8fa)',
        borderRadius: '8px',
        boxShadow: '0 2px 12px rgba(0, 0, 0, 0.08)'
      }}
    >
      {/* Header with current status */}
      <div className="status-header mb-4">
        <Space align="center" style={{ width: '100%', justifyContent: 'space-between' }}>
          <div>
            <Title level={5} style={{ margin: 0 }}>
              {isGenerating ? (
                <Text>
                  <LoadingOutlined style={{ marginRight: 8 }} />
                  Generation in progress
                </Text>
              ) : progress === 100 ? (
                <Text type="success">
                  <CheckCircleOutlined style={{ marginRight: 8 }} />
                  Generation complete
                </Text>
              ) : (
                <Text>
                  <InfoCircleOutlined style={{ marginRight: 8 }} />
                  Status
                </Text>
              )}
            </Title>
            <Text type="secondary">{statusMessage}</Text>
          </div>
          
          {isGenerating && estimatedTimeRemaining && (
            <Tag color="blue">
              Est. time remaining: {estimatedTimeRemaining}
            </Tag>
          )}
        </Space>
      </div>

      {/* Overall Progress bar */}
      {(isGenerating || progress > 0) && (
        <Progress 
          percent={Math.round(progress)} 
          status={isGenerating ? "active" : progress === 100 ? "success" : "normal"}
          strokeColor={{
            '0%': '#108ee9',
            '100%': '#87d068',
          }}
          className="mb-4"
        />
      )}

      {/* Detailed stage progress */}
      {isGenerating && (
        <div className="stage-progress-container mb-4">
          <div style={{
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center', 
            marginBottom: '8px'
          }}>
            <Text strong>{generationStages[currentStageIndex].title}</Text>
            <Text>{Math.round(stageProgress)}%</Text>
          </div>
          
          <Progress 
            percent={Math.round(stageProgress)} 
            status="active"
            strokeColor={{
              '0%': '#722ed1',
              '100%': '#1890ff',
            }}
            size="small"
            className="mb-3"
          />
          
          <Steps
            current={currentStageIndex}
            size="small"
            labelPlacement="vertical"
            style={{ marginTop: '16px' }}
          >
            {generationStages.map((stage, index) => (
              <Step 
                key={index} 
                title={stage.title}
                icon={progress >= stage.threshold ? <CheckCircleOutlined /> : 
                     (index === currentStageIndex ? <LoadingOutlined /> : stage.icon)}
                status={
                  progress >= stage.threshold ? "finish" :
                  index === currentStageIndex ? "process" :
                  index < currentStageIndex ? "wait" : "wait"
                }
                description={`${stage.threshold}%`}
              />
            ))}
          </Steps>
        </div>
      )}

      {/* Prompt display */}
      {prompt && (
        <div className="prompt-display mb-4 p-3" style={{ background: 'rgba(113, 46, 209, 0.05)', borderRadius: '6px', border: '1px solid rgba(113, 46, 209, 0.1)' }}>
          <Text strong style={{ display: 'block', marginBottom: '4px', color: '#722ed1' }}>Prompt:</Text>
          <Paragraph copyable style={{ margin: 0 }}>{prompt}</Paragraph>
        </div>
      )}

      {/* Parameters display */}
      {parameters && Object.keys(parameters).length > 0 && (
        <div className="parameters-display mb-4">
          <Text strong style={{ display: 'block', marginBottom: '4px' }}>Parameters:</Text>
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px' }}>
            {Object.entries(parameters).map(([key, value]) => (
              <Tag key={key} color="orange">
                {key}: {typeof value === 'object' ? JSON.stringify(value) : value.toString()}
              </Tag>
            ))}
          </div>
        </div>
      )}

      {/* Timeline of events */}
      {logs.length > 0 && (
        <div className="log-timeline" style={{ maxHeight: '240px', overflowY: 'auto', paddingRight: '10px' }}>
          <Timeline>
            {logs.map((log, index) => (
              <Timeline.Item 
                key={index} 
                dot={getIcon(log.type)}
              >
                <div className="log-entry">
                  <Text strong>{formatTime(log.timestamp)}</Text>
                  <Text style={{ marginLeft: '8px' }}>{log.message}</Text>
                  
                  {log.data && (
                    <div className="log-data mt-1 ml-4">
                      {typeof log.data === 'string' ? (
                        <Text type="secondary" style={{ fontSize: '12px' }}>{log.data}</Text>
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
      )}
    </Card>
  );
};

export default StatusTracker; 