'use client';

import { useState } from 'react';
import { LogEntry } from '../types';

export const useLogging = () => {
  const [logs, setLogs] = useState<LogEntry[]>([]);
  
  // Add a log entry
  const addLog = (message: string, type: LogEntry['type'] = 'info', data?: any) => {
    const newLog: LogEntry = {
      timestamp: new Date().toISOString(),
      message,
      type,
      data
    };
    
    setLogs(prevLogs => [newLog, ...prevLogs]);
  };
  
  const clearLogs = () => {
    setLogs([]);
  };
  
  return { logs, addLog, clearLogs };
}; 