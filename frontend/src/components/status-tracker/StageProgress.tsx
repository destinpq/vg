'use client';

import React, { useMemo } from 'react';
import { Progress, Typography, Steps } from 'antd';
import { LoadingOutlined, CheckCircleOutlined, SettingOutlined, CloudDownloadOutlined, 
         CodeOutlined, RocketOutlined, ExperimentOutlined, FileImageOutlined, VideoCameraOutlined } from '@ant-design/icons';
import { generationStages } from './types';

const { Text } = Typography;
const { Step } = Steps;

interface StageProgressProps {
  progress: number;
}

// Map of icon names to actual icon components
const iconMap = {
  'setting': <SettingOutlined />,
  'cloud-download': <CloudDownloadOutlined />,
  'code': <CodeOutlined />,
  'rocket': <RocketOutlined />,
  'experiment': <ExperimentOutlined />,
  'file-image': <FileImageOutlined />,
  'video-camera': <VideoCameraOutlined />
};

export const StageProgress: React.FC<StageProgressProps> = ({ progress }) => {
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
                 (index === currentStageIndex ? <LoadingOutlined /> : 
                 iconMap[stage.icon as keyof typeof iconMap])}
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
  );
}; 