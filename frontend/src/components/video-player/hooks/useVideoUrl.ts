'use client';

import { useState, useEffect } from 'react';

export const useVideoUrl = (videoUrl: string) => {
  const [actualUrl, setActualUrl] = useState(videoUrl);
  
  useEffect(() => {
    // Don't replace port 5555, as that's our actual backend server
    let newUrl = videoUrl;
    
    // Support both old and new URL formats
    if (videoUrl.includes('localhost:8000')) {
      newUrl = videoUrl.replace('localhost:8000', 'localhost:5001');
    } else if (videoUrl.includes('localhost:8080')) {
      newUrl = videoUrl.replace('localhost:8080', 'localhost:5001');
    } else if (videoUrl.includes('localhost:50080')) {
      newUrl = videoUrl.replace('localhost:50080', 'localhost:5001');
    } else if (videoUrl.includes('localhost:54321')) {
      newUrl = videoUrl.replace('localhost:54321', 'localhost:5001');
    } else if (videoUrl.includes('localhost:63456')) {
      newUrl = videoUrl.replace('localhost:63456', 'localhost:5001');
    } else if (videoUrl.includes('localhost:5555')) {
      newUrl = videoUrl.replace('localhost:5555', 'localhost:5001');
    }
    
    // Make sure the URL has the /output/ prefix if it's missing
    if ((newUrl.includes('/localhost:5001/') || newUrl.includes('/localhost:5555/')) && !newUrl.includes('/output/')) {
      newUrl = newUrl.replace(/\/localhost:(5001|5555)\//, '/localhost:$1/output/');
    }
    
    console.log('Original video URL:', videoUrl);
    console.log('Actual video URL:', newUrl);
    
    setActualUrl(newUrl);
  }, [videoUrl]);

  return { actualUrl };
}; 