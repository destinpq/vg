'use client';

import React from 'react';
import { Modal, Button, List, Typography, Tag } from 'antd';
import { DeleteOutlined, InfoCircleOutlined } from '@ant-design/icons';
import { CostEntry } from './types';

const { Text } = Typography;

interface CostHistoryModalProps {
  visible: boolean;
  onClose: () => void;
  costHistory: CostEntry[];
  totalHistoricalCost: number;
  currentSessionCost: number;
  currentSessionCalls: number;
  onSaveSession: () => void;
  onClearHistory: () => void;
}

export const CostHistoryModal: React.FC<CostHistoryModalProps> = ({
  visible,
  onClose,
  costHistory,
  totalHistoricalCost,
  currentSessionCost,
  currentSessionCalls,
  onSaveSession,
  onClearHistory
}) => {
  const formatDate = (timestamp: number) => {
    return new Date(timestamp).toLocaleString();
  };

  return (
    <Modal
      title={
        <div className="flex items-center justify-between">
          <span>Cost History</span>
          <Tag color="purple">Total: ₹{totalHistoricalCost + currentSessionCost}</Tag>
        </div>
      }
      open={visible}
      onCancel={onClose}
      footer={[
        <Button key="close" onClick={onClose}>
          Close
        </Button>,
        <Button 
          key="save" 
          type="primary" 
          onClick={onSaveSession}
          disabled={currentSessionCost === 0}
        >
          Save Current Session
        </Button>,
        <Button 
          key="clear" 
          type="default" 
          danger
          icon={<DeleteOutlined />}
          onClick={onClearHistory}
          disabled={costHistory.length === 0}
        >
          Clear History
        </Button>
      ]}
      width={600}
    >
      <div className="mb-4 p-3 bg-purple-50 border border-purple-200 rounded">
        <div className="flex items-center mb-2">
          <InfoCircleOutlined className="mr-2 text-purple-500" />
          <Text strong>Current Session</Text>
        </div>
        <div className="flex justify-between">
          <Text>Cost: <Text strong>₹{currentSessionCost}</Text></Text>
          <Text>API Calls: {currentSessionCalls}</Text>
        </div>
      </div>
      
      {costHistory.length > 0 ? (
        <List
          dataSource={costHistory}
          renderItem={(item) => (
            <List.Item
              key={item.id}
              className="border rounded p-3 mb-2"
            >
              <div className="w-full">
                <div className="flex justify-between">
                  <Text type="secondary">{formatDate(item.timestamp)}</Text>
                  <Text strong className="text-purple-600">₹{item.amount}</Text>
                </div>
                <div className="flex justify-between mt-1">
                  <Text>{item.description}</Text>
                  <Text type="secondary">{item.apiCalls} API calls</Text>
                </div>
              </div>
            </List.Item>
          )}
        />
      ) : (
        <div className="text-center p-6 bg-gray-50 rounded border border-dashed">
          <Text type="secondary">No cost history available</Text>
        </div>
      )}
    </Modal>
  );
}; 