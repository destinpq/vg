'use client';

import { useState } from 'react';
import { EnhancementResult } from '../types';

export const useTopicEnhancement = (
  addLog: (message: string, type: string, data?: any) => void
) => {
  const [enhanceTopic, setEnhanceTopic] = useState(true);

  // Enhance topic with AI
  const enhanceTopicWithAI = async (promptTopic: string): Promise<EnhancementResult> => {
    try {
      addLog('Enhancing conversation topic with AI...', 'loading');
      
      // In a real implementation, call the backend for this
      // For now, simulate an enhanced topic
      const baseTopic = promptTopic.trim();
      
      // Add specific aspects to explore
      const enhanced = `${baseTopic}; exploring historical context, current developments, ethical implications, and future possibilities`;
      
      // Simulate AI processing time
      await new Promise(resolve => setTimeout(resolve, 800));
      
      addLog('Topic enhanced successfully', 'success', { original: baseTopic, enhanced });
      
      return {
        enhanced,
        changes: [
          'exploring historical context',
          'current developments',
          'ethical implications',
          'future possibilities'
        ]
      };
    } catch (error) {
      console.error('Error enhancing topic:', error);
      addLog(`Error enhancing topic: ${error}`, 'error');
      throw error;
    }
  };

  return {
    enhanceTopic,
    setEnhanceTopic,
    enhanceTopicWithAI
  };
}; 