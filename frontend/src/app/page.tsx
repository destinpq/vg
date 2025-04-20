'use client';

import React from 'react';
import { Tabs, Alert } from 'antd';
import VideoGenerator from '../components/VideoGenerator';
import ConversationGenerator from '../components/ConversationGenerator';
import ImageToVideoGenerator from '../components/ImageToVideoGenerator';

const { TabPane } = Tabs;

export default function Home() {
  return (
    <div className="container">
      <h2>Create Amazing AI-Generated Videos</h2>
      <p>Select a generation type below to get started</p>
      
      <Alert
        message={
          <div className="text-center">
            <span className="font-bold">Server Cost Information</span>
            <p>Each server request costs <span style={{ color: "#722ed1", fontWeight: "bold" }}>₹100</span> - you can monitor this cost in real-time!</p>
          </div>
        }
        type="info"
        showIcon
        className="mt-4 mb-4"
        style={{ backgroundColor: "#f9f0ff", borderColor: "#722ed1" }}
      />
      
      <Tabs defaultActiveKey="video" type="card" className="mb-6 mt-4">
        <TabPane tab="Single Videos" key="video">
          <div className="bg-gradient-to-r from-blue-50 to-indigo-50 p-4 rounded-lg mb-6 border border-blue-200">
            <h3 className="text-xl font-bold text-blue-800">✨ AI Video Generation</h3>
            <p className="text-blue-700">
              Generate high-quality AI videos with detailed control over settings. <span className="font-bold">Cost: ₹100 per server request</span>
            </p>
          </div>
          <VideoGenerator />
        </TabPane>
        
        <TabPane tab="Conversation Videos" key="conversation">
          <div className="bg-gradient-to-r from-purple-50 to-pink-50 p-4 rounded-lg mb-6 border border-purple-200">
            <h3 className="text-xl font-bold text-purple-800">🎬 AI Conversation Generator</h3>
            <p className="text-purple-700">
              Generate videos of AI characters having a conversation on any topic. <span className="font-bold">Cost: ₹100 per server request</span>
            </p>
          </div>
          <ConversationGenerator />
        </TabPane>
        
        <TabPane tab="Image to Video" key="i2v">
          <div className="bg-gradient-to-r from-green-50 to-teal-50 p-4 rounded-lg mb-6 border border-green-200">
            <h3 className="text-xl font-bold text-green-800">🖼️ Image to Video Animator</h3>
            <p className="text-green-700">
              Transform still images into high-quality videos with consistent appearance. <span className="font-bold">Cost: ₹100 per server request</span>
            </p>
          </div>
          <ImageToVideoGenerator />
        </TabPane>
      </Tabs>
    </div>
  );
} 