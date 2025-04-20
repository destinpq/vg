'use client';

import React from 'react';
import { Modal, Button, Alert } from 'antd';

interface HelpModalProps {
  onClose: () => void;
}

export const HumanVideoHelpModal: React.FC<HelpModalProps> = ({ onClose }) => {
  return (
    <Modal
      title="Tips for Generating Videos"
      open={true}
      onCancel={onClose}
      footer={[
        <Button key="close" onClick={onClose}>
          Got it!
        </Button>
      ]}
      width={700}
    >
      <div className="space-y-4">
        <div>
          <h3 className="text-lg font-bold">About Video Generation</h3>
          <p>Our system creates high-quality, realistic videos from text prompts. It excels at creating human subjects and realistic scenes.</p>
        </div>
        
        <div>
          <h3 className="text-lg font-bold">Creating Effective Prompts</h3>
          <p>For best results, your prompt should include:</p>
          <ul className="list-disc ml-5">
            <li>Detailed description of subjects (people, objects, scenery)</li>
            <li>Lighting conditions and atmosphere</li>
            <li>Camera angles and movement</li>
            <li>Style references (cinematic, documentary, etc.)</li>
            <li>Quality indicators (high resolution, 8K, detailed, etc.)</li>
          </ul>
        </div>
        
        <div>
          <h3 className="text-lg font-bold">Example Prompts That Work Well:</h3>
          <div className="human-examples">
            <ul className="list-disc ml-5">
              <li>"A cinematic close-up portrait of a young woman with blonde hair smiling at the camera, golden hour lighting, shallow depth of field, shot on ARRI, 8K quality"</li>
              <li>"A businessman in a tailored navy suit walking confidently down a busy city street with glass skyscrapers in the background, cinematic lighting, high detail, telephoto lens"</li>
              <li>"Slow-motion shot of ocean waves crashing against rocky cliffs at sunset, dramatic lighting, hyper-detailed water splashes, cinematic color grading, shot on RED camera"</li>
            </ul>
          </div>
        </div>
        
        <Alert
          message="Important Note"
          description="Videos are limited to 5-10 seconds for best quality. Each API call costs ₹100, and you will see the total cost updating in real-time as your video is generated."
          type="info"
          showIcon
        />
      </div>
    </Modal>
  );
}; 