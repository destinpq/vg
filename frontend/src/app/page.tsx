'use client';

import React from 'react';
import { Tabs } from 'antd';
import VideoGenerator from '../components/VideoGenerator';
import ConversationGenerator from '../components/ConversationGenerator';
import ImageToVideoGenerator from '../components/ImageToVideoGenerator';
import DevotionalVideoGenerator from '../components/DevotionalVideoGenerator';

const { TabPane } = Tabs;

export default function Home() {
  return (
    <div className="container">
      <h2>Create Amazing AI-Generated Videos</h2>
      <p>Select a generation type below to get started</p>
      
      <Tabs defaultActiveKey="video" type="card" className="mb-6 mt-4">
        <TabPane tab="Single Videos" key="video">
          <div className="bg-gradient-to-r from-blue-50 to-indigo-50 p-4 rounded-lg mb-6 border border-blue-200">
            <h3 className="text-xl font-bold text-blue-800">✨ NEW: Realistic Human Videos</h3>
            <p className="text-blue-700">
              Enable the "Human Focus" option to generate realistic human videos with our improved models!
            </p>
          </div>
          <VideoGenerator />
        </TabPane>
        
        <TabPane tab="Devotional Content" key="devotional">
          <div className="bg-gradient-to-r from-indigo-50 to-blue-50 p-4 rounded-lg mb-6 border border-indigo-200">
            <h3 className="text-xl font-bold text-indigo-800">🕊️ NEW: Devotional Video Generator</h3>
            <p className="text-indigo-700">
              Create spiritually meaningful videos for worship, meditation, prayer backgrounds, and religious content!
            </p>
          </div>
          <DevotionalVideoGenerator />
        </TabPane>
        
        <TabPane tab="Conversation Videos" key="conversation">
          <div className="bg-gradient-to-r from-purple-50 to-pink-50 p-4 rounded-lg mb-6 border border-purple-200">
            <h3 className="text-xl font-bold text-purple-800">🎬 NEW: AI Conversation Generator</h3>
            <p className="text-purple-700">
              Generate videos of two AI characters having a conversation on any topic with subtitles and lip sync!
            </p>
          </div>
          <ConversationGenerator />
        </TabPane>
        
        <TabPane tab="Image to Video" key="i2v">
          <div className="bg-gradient-to-r from-green-50 to-teal-50 p-4 rounded-lg mb-6 border border-green-200">
            <h3 className="text-xl font-bold text-green-800">🖼️ NEW: Image to Video Animator</h3>
            <p className="text-green-700">
              Transform still images into high-quality videos with consistent character appearance and motion!
            </p>
          </div>
          <ImageToVideoGenerator />
        </TabPane>
      </Tabs>
    </div>
  );
} 