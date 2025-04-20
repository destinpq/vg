'use client';

import { useState, useEffect, useCallback } from 'react';
import { Modal } from 'antd';
import { CostEntry } from '../types';

export const useCostHistory = (currentSessionCost: number, currentSessionCalls: number) => {
  const [costHistory, setCostHistory] = useState<CostEntry[]>([]);
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

  const saveCurrentSession = useCallback(() => {
    if (currentSessionCost <= 0) return;
    
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
  }, [costHistory, currentSessionCost, currentSessionCalls]);

  const clearHistory = useCallback(() => {
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
  }, []);

  return {
    costHistory,
    totalHistoricalCost,
    saveCurrentSession,
    clearHistory
  };
}; 