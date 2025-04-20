'use client';

import React, { useState, useEffect } from 'react';
import { Button } from 'antd';
import { HistoryOutlined } from '@ant-design/icons';
import { CostHistoryModal } from './CostHistoryModal';
import { useCostHistory } from './hooks/useCostHistory';

interface CostHistoryProps {
  currentSessionCost: number;
  currentSessionCalls: number;
}

const CostHistory: React.FC<CostHistoryProps> = ({ 
  currentSessionCost, 
  currentSessionCalls 
}) => {
  const [visible, setVisible] = useState(false);
  const { costHistory, totalHistoricalCost, saveCurrentSession, clearHistory } = useCostHistory(currentSessionCost, currentSessionCalls);
  
  // Save current session cost when component unmounts
  useEffect(() => {
    return () => {
      if (currentSessionCost > 0) {
        saveCurrentSession();
      }
    };
  }, [currentSessionCost, currentSessionCalls, saveCurrentSession]);

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
      
      {visible && (
        <CostHistoryModal
          visible={visible}
          onClose={() => setVisible(false)}
          costHistory={costHistory}
          totalHistoricalCost={totalHistoricalCost}
          currentSessionCost={currentSessionCost}
          currentSessionCalls={currentSessionCalls}
          onSaveSession={saveCurrentSession}
          onClearHistory={clearHistory}
        />
      )}
    </>
  );
};

export default CostHistory; 