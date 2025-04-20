'use client';

import React from 'react';

export const VideoGeneratorBanner: React.FC = () => {
  return (
    <div className="mb-4 bg-purple-800 text-white p-3 rounded-lg shadow-lg">
      <div className="flex items-center justify-between">
        <div className="flex items-center">
          <span className="text-xl mr-2">🚀</span>
          <h3 className="font-bold text-lg m-0">REPLICATE API MODE</h3>
        </div>
        <div className="text-xs bg-purple-700 px-2 py-1 rounded">₹100 per API call</div>
      </div>
      <p className="text-sm mt-1 mb-0">All video generation uses Replicate's H100 GPU (cost tracking enabled)</p>
    </div>
  );
}; 