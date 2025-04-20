'use client';

import React, { useState, useEffect } from 'react';
import { Card, List, Typography, Button, Modal, Tag } from 'antd';
import { HistoryOutlined, DeleteOutlined, InfoCircleOutlined } from '@ant-design/icons';

const { Title, Text } = Typography;

interface CostEntry {
  id: string;
  timestamp: number;
  amount: number;
  apiCalls: number;
  description: string;
}

interface CostHistoryProps {
  currentSessionCost: number;
  currentSessionCalls: number;
}

const CostHistory: React.FC<CostHistoryProps> = ({ 
  currentSessionCost, 
  currentSessionCalls 
}) => {
  const [costHistory, setCostHistory] = useState<CostEntry[]>([]);
  const [visible, setVisible] = useState(false);
  const [totalHistoricalCost, setTotalHistoricalCost] = useState(0);

  // Load cost history from localStorage on component mount
  useEffect(() => {
    const savedHistory = localStorage.getItem('costHistory');
    if (savedHistory) {
      try {
        const parsedHistory = JSON.parse(savedHistory) as CostEntry[];
        setCostHistory(parsedHistory);
        
        // Calculate total historical cost
        const total = parsedHistory.reduce((sum, entry) => sum + entry.amount, 0);
        setTotalHistoricalCost(total);
      } catch (e) {
        console.error('Error parsing cost history:', e);
      }
    }
  }, []);

  // Save current session cost when component unmounts
  useEffect(() => {
    return () => {
      if (currentSessionCost > 0) {
        saveCurrentSession();
      }
    };
  }, [currentSessionCost, currentSessionCalls]);

  const saveCurrentSession = () => {
    const newEntry: CostEntry = {
      id: `session-${Date.now()}`,
      timestamp: Date.now(),
      amount: currentSessionCost,
      apiCalls: currentSessionCalls,
      description: `Video generation (${currentSessionCalls} API calls)`
    };

    const updatedHistory = [...costHistory, newEntry];
    setCostHistory(updatedHistory);
    localStorage.setItem('costHistory', JSON.stringify(updatedHistory));
    
    // Update total cost
    setTotalHistoricalCost(prev => prev + currentSessionCost);
  };

  const clearHistory = () => {
    Modal.confirm({
      title: 'Clear Cost History',
      content: 'Are you sure you want to clear all cost history? This cannot be undone.',
      okText: 'Yes, Clear History',
      okType: 'danger',
      cancelText: 'Cancel',
      onOk() {
        setCostHistory([]);
        localStorage.removeItem('costHistory');
        setTotalHistoricalCost(0);
      }
    });
  };

  const formatDate = (timestamp: number) => {
    return new Date(timestamp).toLocaleString();
  };

  return (
    <>
      <Button 
        type="default" 
        icon={<HistoryOutlined />} 
        onClick={() => setVisible(true)}
        className="cost-history-button"
      >
        Cost History
      </Button>
      
      <Modal
        title={
          <div className="flex items-center justify-between">
            <span>Cost History</span>
            <Tag color="purple">Total: ₹{totalHistoricalCost + currentSessionCost}</Tag>
          </div>
        }
        open={visible}
        onCancel={() => setVisible(false)}
        footer={[
          <Button key="close" onClick={() => setVisible(false)}>
            Close
          </Button>,
          <Button 
            key="save" 
            type="primary" 
            onClick={saveCurrentSession}
            disabled={currentSessionCost === 0}
          >
            Save Current Session
          </Button>,
          <Button 
            key="clear" 
            type="default" 
            danger
            icon={<DeleteOutlined />}
            onClick={clearHistory}
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
    </>
  );
};

export default CostHistory; 