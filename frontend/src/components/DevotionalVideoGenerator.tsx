'use client';

import React, { useState, useRef, useEffect } from 'react';
import { Input, Button, Progress, Card, Alert, Select, Spin, Slider, Row, Col, Space, Typography, Switch, Modal, Tooltip, Tag, message } from 'antd';
import { CloudUploadOutlined, VideoCameraOutlined, LoadingOutlined, InfoCircleOutlined, QuestionCircleOutlined, ApiOutlined } from '@ant-design/icons';

const { Title, Text, Paragraph } = Typography;
const { Option } = Select;

// Helper function for API calls
const apiCall = async (endpoint: string, options = {}) => {
  // Use the environment variable for our backend server
  const baseUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
  const url = `${baseUrl}${endpoint}`;
  
  console.log(`Making API call to: ${url}`);
  
  const defaultOptions = {
    headers: {
      'Content-Type': 'application/json',
      'Accept': 'application/json',
      'Cache-Control': 'no-cache',
    },
    mode: 'cors' as RequestMode,
  };
  
  try {
    console.log('Starting fetch request...');
    const response = await fetch(url, { ...defaultOptions, ...options });
    console.log(`Response status: ${response.status}`);
    
    if (!response.ok) {
      const errorText = await response.text();
      console.error(`API error (${response.status}): ${errorText}`);
      
      // Special handling for 404 errors on status endpoint after completion
      if (response.status === 404 && endpoint.includes('/video/job-status/')) {
        // If the video was already marked as completed, just return gracefully
        if (localStorage.getItem(`video_completed_${endpoint.split('/').pop()}`)) {
          const mockResponse = {
            ok: true,
            status: 200,
            statusText: "OK",
            headers: new Headers(),
            json: () => Promise.resolve({ status: 'completed' })
          } as unknown as Response;
          return mockResponse;
        }
      }
      
      throw new Error(`API error: ${response.status} - ${errorText || response.statusText}`);
    }
    
    return response;
  } catch (error) {
    console.error('API call error:', error);
    throw error;
  }
};

// Devotional content categories
const devotionalCategories = [
  { value: 'scripture', label: 'Scripture Visualization' },
  { value: 'worship', label: 'Worship Moments' },
  { value: 'nature', label: 'Divine Nature' },
  { value: 'prayer', label: 'Prayer Spaces' },
  { value: 'symbol', label: 'Religious Symbols' },
  { value: 'event', label: 'Religious Events' },
];

// Religious traditions
const religiousTraditions = [
  { value: 'christian', label: 'Christian' },
  { value: 'hindu', label: 'Hindu' },
  { value: 'buddhist', label: 'Buddhist' },
  { value: 'islamic', label: 'Islamic' },
  { value: 'jewish', label: 'Jewish' },
  { value: 'interfaith', label: 'Interfaith/Universal' },
];

// Devotional themes
const devotionalThemes = [
  { value: 'peace', label: 'Peace & Serenity' },
  { value: 'hope', label: 'Hope & Inspiration' },
  { value: 'love', label: 'Divine Love' },
  { value: 'wisdom', label: 'Wisdom & Guidance' },
  { value: 'gratitude', label: 'Gratitude & Blessings' },
  { value: 'community', label: 'Faith Community' },
];

// Enhances prompt specifically for devotional content
const enhanceDevotionalPrompt = (
  prompt: string, 
  category: string, 
  tradition: string, 
  theme: string,
  style: string
): { enhancedPrompt: string, logs: any[] } => {
  const logs = [];
  
  // Log the original prompt
  logs.push({
    level: 'info',
    message: `Original prompt: "${prompt}"`,
    time: new Date().toLocaleTimeString()
  });
  
  // Analyze prompt for elements
  const hasSymbols = /cross|crucifix|menorah|om|buddha|lotus|star of david|crescent|prayer beads|shrine|altar/i.test(prompt);
  const hasScenery = /temple|church|mosque|synagogue|sanctuary|cathedral|nature|mountain|river|garden|sacred space/i.test(prompt);
  const hasLight = /light|ray|beam|glow|shine|illumination|divine light|radiance|aura/i.test(prompt);
  const hasCamera = /camera|angle|zoom|pan|aerial|tracking/i.test(prompt);

  // Create enhanced prompt based on the original and detected elements
  let enhancedPrompt = prompt;
  let additions = [];

  // Add tradition-specific elements
  if (tradition === 'christian') {
    if (!prompt.toLowerCase().includes('christian')) {
      additions.push("Christian-inspired");
    }
    if (!hasSymbols && !prompt.toLowerCase().includes('cross')) {
      additions.push(category === 'symbol' ? "with prominent cross symbol" : "with subtle cross imagery");
      logs.push({
        level: 'info',
        message: 'Added Christian symbolism',
        time: new Date().toLocaleTimeString()
      });
    }
  } else if (tradition === 'hindu') {
    if (!prompt.toLowerCase().includes('hindu')) {
      additions.push("Hindu-inspired");
    }
    if (!hasSymbols && !prompt.toLowerCase().includes('om')) {
      additions.push(category === 'symbol' ? "with prominent Om symbol" : "with subtle Hindu iconography");
      logs.push({
        level: 'info',
        message: 'Added Hindu symbolism',
        time: new Date().toLocaleTimeString()
      });
    }
  } else if (tradition === 'buddhist') {
    if (!prompt.toLowerCase().includes('buddhist')) {
      additions.push("Buddhist-inspired");
    }
    if (!hasSymbols && !prompt.toLowerCase().includes('buddha')) {
      additions.push(category === 'symbol' ? "with lotus flower symbolism" : "with peaceful Buddhist elements");
      logs.push({
        level: 'info',
        message: 'Added Buddhist symbolism',
        time: new Date().toLocaleTimeString()
      });
    }
  } else if (tradition === 'islamic') {
    if (!prompt.toLowerCase().includes('islamic')) {
      additions.push("Islamic-inspired");
    }
    if (!hasSymbols && !prompt.toLowerCase().includes('crescent')) {
      additions.push(category === 'symbol' ? "with geometric Islamic patterns" : "with subtle Islamic architectural elements");
      logs.push({
        level: 'info',
        message: 'Added Islamic symbolism',
        time: new Date().toLocaleTimeString()
      });
    }
  } else if (tradition === 'jewish') {
    if (!prompt.toLowerCase().includes('jewish')) {
      additions.push("Jewish-inspired");
    }
    if (!hasSymbols && !prompt.toLowerCase().includes('star')) {
      additions.push(category === 'symbol' ? "with Star of David symbol" : "with subtle Jewish symbolism");
      logs.push({
        level: 'info',
        message: 'Added Jewish symbolism',
        time: new Date().toLocaleTimeString()
      });
    }
  } else if (tradition === 'interfaith') {
    additions.push("universal spiritual symbols");
    logs.push({
      level: 'info',
      message: 'Added interfaith/universal symbolism',
      time: new Date().toLocaleTimeString()
    });
  }

  // Add category-specific elements
  if (category === 'scripture') {
    if (!prompt.toLowerCase().includes('scripture') && !prompt.toLowerCase().includes('text')) {
      additions.push("with sacred text or scripture");
      logs.push({
        level: 'info',
        message: 'Added scripture elements',
        time: new Date().toLocaleTimeString()
      });
    }
  } else if (category === 'worship') {
    if (!prompt.toLowerCase().includes('worship')) {
      additions.push("devotional worship scene");
      logs.push({
        level: 'info',
        message: 'Added worship elements',
        time: new Date().toLocaleTimeString()
      });
    }
  } else if (category === 'nature') {
    if (!prompt.toLowerCase().includes('nature')) {
      additions.push("divine beauty of nature");
      logs.push({
        level: 'info',
        message: 'Added divine nature elements',
        time: new Date().toLocaleTimeString()
      });
    }
  } else if (category === 'prayer') {
    if (!prompt.toLowerCase().includes('prayer')) {
      additions.push("peaceful prayer environment");
      logs.push({
        level: 'info',
        message: 'Added prayer space elements',
        time: new Date().toLocaleTimeString()
      });
    }
  }

  // Add theme elements
  if (theme === 'peace') {
    additions.push("serene and peaceful atmosphere");
    logs.push({
      level: 'info',
      message: 'Added peace theme',
      time: new Date().toLocaleTimeString()
    });
  } else if (theme === 'hope') {
    additions.push("uplifting and hopeful mood");
    logs.push({
      level: 'info',
      message: 'Added hope theme',
      time: new Date().toLocaleTimeString()
    });
  } else if (theme === 'love') {
    additions.push("divine love radiating");
    logs.push({
      level: 'info',
      message: 'Added divine love theme',
      time: new Date().toLocaleTimeString()
    });
  } else if (theme === 'wisdom') {
    additions.push("profound spiritual wisdom");
    logs.push({
      level: 'info',
      message: 'Added wisdom theme',
      time: new Date().toLocaleTimeString()
    });
  } else if (theme === 'gratitude') {
    additions.push("grateful and blessed feeling");
    logs.push({
      level: 'info',
      message: 'Added gratitude theme',
      time: new Date().toLocaleTimeString()
    });
  }

  // Add light elements if not present
  if (!hasLight) {
    additions.push("with divine light rays");
    logs.push({
      level: 'info',
      message: 'Added divine light elements',
      time: new Date().toLocaleTimeString()
    });
  }

  // Add camera movement if not present
  if (!hasCamera) {
    if (style === 'cinematic') {
      additions.push("with slow reverent camera movement");
    } else {
      additions.push("with steady contemplative camera");
    }
    logs.push({
      level: 'info',
      message: 'Added appropriate camera movement',
      time: new Date().toLocaleTimeString()
    });
  }

  // Add style-specific enhancements
  if (style === 'cinematic' && !prompt.toLowerCase().includes('cinematic')) {
    additions.push("cinematic quality");
    logs.push({
      level: 'info',
      message: 'Added cinematic quality specification',
      time: new Date().toLocaleTimeString()
    });
  } else if (style === 'artistic' && !prompt.toLowerCase().includes('artistic')) {
    additions.push("artistic style");
    logs.push({
      level: 'info',
      message: 'Added artistic style specification',
      time: new Date().toLocaleTimeString()
    });
  }

  // Add quality enhancement
  additions.push("high quality, detailed, spiritually evocative");

  // Add the enhancements to the prompt
  // Check if prompt ends with punctuation
  const endsWithPunctuation = /[,.!?]$/.test(enhancedPrompt);
  
  if (endsWithPunctuation) {
    // Remove the punctuation first
    enhancedPrompt = enhancedPrompt.replace(/[,.!?]$/, '');
  }
  
  // Add the enhancements
  enhancedPrompt += `, ${additions.join(", ")}`;
  
  // Add back period at the end
  if (!enhancedPrompt.endsWith('.')) {
    enhancedPrompt += '.';
  }
  
  logs.push({
    level: 'success',
    message: `Enhanced devotional prompt: "${enhancedPrompt}"`,
    time: new Date().toLocaleTimeString()
  });
  
  return {
    enhancedPrompt: enhancedPrompt,
    logs: logs
  };
};

// Helper function for OpenAI calls
const enhancePromptWithOpenAI = async (
  prompt: string,
  category: string,
  tradition: string,
  theme: string,
  style: string
): Promise<{ enhancedPrompt: string, logs: any[] }> => {
  const logs = [];
  
  logs.push({
    level: 'info',
    message: `Original prompt: "${prompt}"`,
    time: new Date().toLocaleTimeString()
  });
  
  logs.push({
    level: 'info',
    message: `Sending to OpenAI for advanced enhancement...`,
    time: new Date().toLocaleTimeString()
  });

  try {
    // Construct a detailed system prompt for OpenAI
    const systemPrompt = `You are a specialist in creating detailed, accurate, and spiritually appropriate video generation prompts.
Your task is to enhance a user's prompt to generate a high-quality devotional video using AI video generation technology (based on Tencent Hunyuan Video).

USER SPECIFICATIONS:
- Religious Tradition: ${tradition}
- Devotional Category: ${category}
- Spiritual Theme: ${theme}
- Visual Style: ${style}

ENHANCEMENT GUIDELINES:
1. Preserve the core imagery and intention of the original prompt
2. Add appropriate religious symbolism and imagery relevant to the specified tradition
3. Incorporate visual elements that evoke the specified spiritual theme
4. Add details about lighting, atmosphere, and camera movements appropriate for devotional content
5. Ensure the language is respectful and appropriate for religious/spiritual content
6. Add specific details that will help the AI video generator create a high-quality result
7. Avoid direct representation of deities or prophets where this would be culturally inappropriate
8. Make the prompt more specific, vivid, and detailed, emphasizing the spiritual aspects

Return ONLY the enhanced prompt text with no additional commentary, explanations, or formatting.`;

    // Make the API call to OpenAI
    const response = await fetch('https://api.openai.com/v1/chat/completions', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${process.env.NEXT_PUBLIC_OPENAI_API_KEY || localStorage.getItem('openai_api_key')}`
      },
      body: JSON.stringify({
        model: "gpt-3.5-turbo",
        messages: [
          {
            role: "system",
            content: systemPrompt
          },
          {
            role: "user",
            content: prompt
          }
        ],
        temperature: 0.7,
        max_tokens: 300
      })
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(`OpenAI API error: ${JSON.stringify(errorData)}`);
    }

    const data = await response.json();
    const enhancedPrompt = data.choices[0].message.content.trim();

    logs.push({
      level: 'success',
      message: `OpenAI enhancement successful`,
      time: new Date().toLocaleTimeString()
    });

    logs.push({
      level: 'success',
      message: `Enhanced prompt: "${enhancedPrompt}"`,
      time: new Date().toLocaleTimeString()
    });

    return {
      enhancedPrompt,
      logs
    };
  } catch (error) {
    logs.push({
      level: 'error',
      message: `OpenAI enhancement failed: ${error.message}`,
      time: new Date().toLocaleTimeString()
    });

    // Fall back to our rule-based enhancement
    logs.push({
      level: 'warning',
      message: 'Falling back to built-in enhancement system',
      time: new Date().toLocaleTimeString()
    });

    const fallbackEnhancement = enhanceDevotionalPrompt(prompt, category, tradition, theme, style);
    
    return {
      enhancedPrompt: fallbackEnhancement.enhancedPrompt,
      logs: [...logs, ...fallbackEnhancement.logs]
    };
  }
};

export default function DevotionalVideoGenerator() {
  // State
  const [prompt, setPrompt] = useState('');
  const [videoUrl, setVideoUrl] = useState('');
  const [videoId, setVideoId] = useState('');
  const [isGenerating, setIsGenerating] = useState(false);
  const [error, setError] = useState('');
  const [statusMessage, setStatusMessage] = useState('');
  const [pollingActive, setPollingActive] = useState(false);
  const [progress, setProgress] = useState(0);
  const [apiCallCount, setApiCallCount] = useState(0);
  const [diffusionStep, setDiffusionStep] = useState('');
  
  // Devotional content settings
  const [devotionalCategory, setDevotionalCategory] = useState('scripture');
  const [religiousTradition, setReligiousTradition] = useState('christian');
  const [devotionalTheme, setDevotionalTheme] = useState('peace');
  
  // Video settings
  const [duration, setDuration] = useState(5);
  const [quality, setQuality] = useState('high');
  const [style, setStyle] = useState('cinematic');
  const [showHelpModal, setShowHelpModal] = useState(false);
  
  const videoRef = useRef<HTMLVideoElement>(null);

  // Add OpenAI API settings
  const [openAIKey, setOpenAIKey] = useState('');
  const [useOpenAI, setUseOpenAI] = useState(false);
  const [showAPIModal, setShowAPIModal] = useState(false);

  // Add state for storing and displaying the enhanced prompt
  const [originalPrompt, setOriginalPrompt] = useState('');
  const [enhancedPromptDisplay, setEnhancedPromptDisplay] = useState('');
  const [showPromptComparison, setShowPromptComparison] = useState(false);

  // Poll for video status when videoId is available
  useEffect(() => {
    if (!videoId || !pollingActive) return;
    
    setStatusMessage('Initializing devotional video generation...');
    
    // Store the video ID for potential 404 handling
    const currentVideoId = videoId;
    
    const intervalId = setInterval(async () => {
      try {
        // Increment API call counter
        setApiCallCount(prev => prev + 1);
        
        // Use the Flask status endpoint with model_id and prediction_id
        const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
        // The Flask API expects /status/model_id/prediction_id
        const statusUrl = `${apiUrl}/status/default-model/${currentVideoId}`;
        
        const response = await fetch(statusUrl, {
          method: 'GET',
          headers: {
            'Accept': 'application/json'
          }
        });
        
        if (!response.ok) {
          throw new Error(`Status API error: ${response.status}`);
        }
        
        const data = await response.json();
        console.log('Video status:', data);
        
        // Update progress if available
        if (data.progress) {
          setProgress(data.progress);
        }
        
        // Extract diffusion step information if available
        if (data.message && data.message.includes("Diffusion step")) {
          try {
            const stepMatch = /Diffusion step (\d+)\/(\d+)/.exec(data.message);
            if (stepMatch) {
              setDiffusionStep(`${stepMatch[1]}/${stepMatch[2]}`);
            }
          } catch (e) {
            console.error("Error parsing diffusion step", e);
          }
        }
        
        // Check all possible status values from the Flask API
        if (data.status === 'completed' || data.status === 'succeeded') {
          // For a completed video in Flask, check for the output
          if (data.video_url) {
            setVideoUrl(data.video_url);
          } else {
            // If no direct URL, we need to construct it
            setVideoUrl(`${apiUrl}/outputs/default-model/${currentVideoId}`);
          }
          
          setIsGenerating(false);
          setStatusMessage('');
          setPollingActive(false);
          setProgress(100);
          // Mark this video as completed in localStorage to handle 404s later
          localStorage.setItem(`video_completed_${currentVideoId}`, 'true');
          clearInterval(intervalId);
        } else if (data.status === 'failed') {
          setError(`Video generation failed: ${data.message || data.error || data.logs || 'Unknown error'}`);
          setIsGenerating(false);
          setStatusMessage('');
          setPollingActive(false);
          clearInterval(intervalId);
        } else if (data.status === 'processing') {
          // Use progress information if available
          if (data.progress) {
            if (data.message && data.message.includes("Diffusion step")) {
              setStatusMessage(`${data.message}`);
            } else {
              setStatusMessage(`Processing your devotional video... ${Math.round(data.progress)}% complete. ${data.message || ''}`);
            }
          } else {
            setStatusMessage('Processing your devotional video...');
          }
        } else if (data.status === 'queued' || data.status === 'pending') {
          setStatusMessage('Your devotional video is queued and will start processing soon...');
        }
      } catch (err) {
        console.error('Error checking status:', err);
        
        // Check if we already have a video URL
        if (videoUrl) {
          // If we have a URL but got an error, stop polling - video is ready
          setPollingActive(false);
          clearInterval(intervalId);
        } else {
          setStatusMessage('Checking status...');
        }
      }
    }, 2000);
    
    return () => {
      clearInterval(intervalId);
      setPollingActive(false);
    };
  }, [videoId, pollingActive, videoUrl]);

  // Check for saved OpenAI API key on mount
  useEffect(() => {
    const savedKey = localStorage.getItem('openai_api_key');
    if (savedKey) {
      setOpenAIKey(savedKey);
      setUseOpenAI(true);
    }
  }, []);

  // Generate devotional video
  const handleGenerateVideo = async () => {
    if (!prompt.trim()) return;

    setIsGenerating(true);
    setError('');
    setVideoUrl('');
    setProgress(0);
    setApiCallCount(0);
    setDiffusionStep('');
    setStatusMessage('Analyzing your devotional prompt...');
    // Save the original prompt for comparison
    setOriginalPrompt(prompt.trim());
    
    try {
      // Determine which enhancement method to use
      let enhancedResult;
      
      if (useOpenAI && openAIKey) {
        // Use OpenAI for advanced prompt enhancement
        setStatusMessage('Using OpenAI to create sophisticated devotional script...');
        enhancedResult = await enhancePromptWithOpenAI(
          prompt,
          devotionalCategory,
          religiousTradition,
          devotionalTheme,
          style
        );
      } else {
        // Use built-in rule-based enhancement
        setStatusMessage('Enhancing your devotional prompt...');
        enhancedResult = enhanceDevotionalPrompt(
          prompt, 
          devotionalCategory, 
          religiousTradition, 
          devotionalTheme,
          style
        );
      }
      
      const enhancedPrompt = enhancedResult.enhancedPrompt;
      const promptLogs = enhancedResult.logs;
      
      // Save the enhanced prompt for display
      setEnhancedPromptDisplay(enhancedPrompt);
      setShowPromptComparison(true);
      
      // Log the analysis
      console.log('Original prompt:', prompt);
      console.log('Enhanced devotional prompt:', enhancedPrompt);
      console.log('Category:', devotionalCategory);
      console.log('Tradition:', religiousTradition);
      console.log('Theme:', devotionalTheme);
      
      // Update UI with analysis results
      setStatusMessage('Creating spiritually evocative video from your enhanced prompt...');
      
      // Create URL parameters 
      const params = new URLSearchParams({
        prompt: enhancedPrompt,
        duration: duration.toString(),
        quality: quality,
        style: style,
        force_replicate: 'true',
        use_hunyuan: 'false',
        human_focus: 'true'
      });
      
      // Make the API call
      // Use the video endpoint directly with the Flask backend
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
      const endpoint = `/video`;
      
      // Use the POST endpoint instead of GET for the Flask server
      const response = await fetch(`${apiUrl}${endpoint}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json'
        },
        body: JSON.stringify({
          model_id: 'default-model',
          prompt: enhancedPrompt,
          duration: duration,
          quality: quality,
          style: style,
          force_replicate: true,
          use_hunyuan: false,
          human_focus: true
        })
      });
      
      if (!response.ok) {
        throw new Error(`API error: ${response.status}`);
      }
      
      const data = await response.json();
      console.log('Devotional video generation response:', data);
      
      // Handle the response
      if (data.error) {
        setError(`Video Generation Error: ${data.error}`);
        setIsGenerating(false);
        return;
      }
      
      // Set video ID for status polling
      setVideoId(data.id);
      setPollingActive(true);
      setStatusMessage('Starting devotional video generation...');
      
      // If video is already completed in the response
      if (data.status === 'completed' && data.video_url) {
        setVideoUrl(data.video_url);
        setIsGenerating(false);
        setStatusMessage('✨ Devotional video created successfully!');
        setPollingActive(false);
      }
    } catch (err: any) {
      const errorMessage = err.message || 'Unknown error';
      setError(`An error occurred: ${errorMessage}`);
      console.error('Error in devotional video generation:', err);
      setIsGenerating(false);
      setStatusMessage('');
    }
  };

  // Help modal content
  const DevotionalHelpModal = () => (
    <Modal
      title="Tips for Creating Devotional Videos"
      open={showHelpModal}
      onCancel={() => setShowHelpModal(false)}
      footer={[
        <Button key="close" onClick={() => setShowHelpModal(false)}>
          Got it!
        </Button>
      ]}
      width={700}
    >
      <div className="space-y-4">
        <div>
          <h3 className="text-lg font-bold">About Devotional Video Generator</h3>
          <p>This tool specializes in creating spiritually evocative videos that can be used for worship, meditation, prayer backgrounds, and religious content.</p>
        </div>
        
        <div>
          <h3 className="text-lg font-bold">Creating Effective Devotional Prompts</h3>
          <p>For best results, your prompt should include:</p>
          <ul className="list-disc ml-5">
            <li>Specific religious imagery or symbols relevant to your tradition</li>
            <li>The mood or feeling you want to evoke (peaceful, joyful, contemplative)</li>
            <li>Any specific scripture or religious text you want to visualize</li>
            <li>Sacred spaces or natural settings that complement your devotional theme</li>
          </ul>
        </div>
        
        <div>
          <h3 className="text-lg font-bold">Example Prompts That Work Well:</h3>
          <div className="devotional-examples">
            <ul className="list-disc ml-5">
              <li>"A peaceful garden with sunlight streaming through trees, evoking the presence of God"</li>
              <li>"Ancient temple with sacred texts illuminated by candlelight"</li>
              <li>"Mountain landscape with divine light rays breaking through clouds"</li>
              <li>"Serene meditation space with lotus flowers and gentle water"</li>
              <li>"Church interior with stained glass windows casting colorful light"</li>
            </ul>
          </div>
        </div>
        
        <Alert
          message="Important Note"
          description="Our system will enhance your prompt with appropriate religious and spiritual elements based on your selected tradition and theme. The AI will avoid creating direct representations of deities or prophets in accordance with respectful practices."
          type="info"
          showIcon
        />
      </div>
    </Modal>
  );

  // OpenAI API settings modal
  const OpenAISettingsModal = () => (
    <Modal
      title="Configure OpenAI Integration"
      open={showAPIModal}
      onCancel={() => setShowAPIModal(false)}
      footer={[
        <Button key="close" onClick={() => setShowAPIModal(false)}>
          Close
        </Button>
      ]}
      width={600}
    >
      <div className="space-y-4">
        <Alert
          message="Enhanced Prompt Generation with OpenAI"
          description="Connect your OpenAI API key to enable advanced prompt enhancement. This will create more detailed and accurate devotional video scripts."
          type="info"
          showIcon
        />
        
        <div className="mt-4">
          <Text strong>OpenAI API Key:</Text>
          <Input.Password
            value={openAIKey}
            onChange={(e) => setOpenAIKey(e.target.value)}
            placeholder="Enter your OpenAI API key"
            className="mt-1"
          />
          <Text type="secondary" className="block mt-1 text-xs">
            Your API key is stored only in your browser's local storage and is never sent to our servers.
          </Text>
        </div>
        
        <div className="mt-4">
          <Button
            type="primary"
            onClick={() => {
              if (openAIKey) {
                localStorage.setItem('openai_api_key', openAIKey);
                setUseOpenAI(true);
                setShowAPIModal(false);
                message.success('OpenAI API key saved successfully!');
              } else {
                message.error('Please enter a valid API key');
              }
            }}
          >
            Save API Key
          </Button>
          
          <Button
            type="default"
            className="ml-2"
            onClick={() => {
              localStorage.removeItem('openai_api_key');
              setOpenAIKey('');
              setUseOpenAI(false);
              message.info('OpenAI API key removed');
            }}
          >
            Clear API Key
          </Button>
        </div>
      </div>
    </Modal>
  );

  return (
    <div className="max-w-4xl mx-auto p-6">
      {/* Devotional mode banner */}
      <div className="mb-4 bg-indigo-800 text-white p-3 rounded-lg shadow-lg">
        <div className="flex items-center justify-between">
          <div className="flex items-center">
            <span className="text-xl mr-2">✨</span>
            <h3 className="font-bold text-lg m-0">DEVOTIONAL VIDEO GENERATOR</h3>
          </div>
          <div className="text-xs bg-indigo-700 px-2 py-1 rounded">POWERED BY REPEATIT</div>
        </div>
        <p className="text-sm mt-1 mb-0">Create spiritually evocative videos for worship, meditation, and religious content</p>
      </div>
      
      <Card className="shadow-lg rounded-lg">
        <div className="flex justify-between items-center mb-6">
          <Title level={2} className="m-0">Devotional Video Generator</Title>
          <div>
            <Button 
              type={useOpenAI ? "primary" : "default"}
              icon={<ApiOutlined />}
              onClick={() => setShowAPIModal(true)}
              className="mr-2"
            >
              {useOpenAI ? "OpenAI Connected ✓" : "Connect OpenAI"}
            </Button>
            <Button 
              type="text" 
              icon={<QuestionCircleOutlined style={{ fontSize: '22px' }} />} 
              onClick={() => setShowHelpModal(true)}
              size="large"
            />
          </div>
        </div>
        
        <Alert
          message="Create Devotional Videos"
          description={
            <div>
              <p className="mb-2">This specialized generator creates videos infused with spiritual meaning and devotional elements:</p>
              <ol className="list-decimal ml-5">
                <li className="mb-1">Select your religious tradition and devotional theme</li>
                <li className="mb-1">Enter a prompt describing the spiritual imagery you want</li>
                <li className="mb-1">Our system will enhance your prompt with appropriate devotional elements</li>
                <li className="mb-1">Generate a video that evokes spiritual connection and meaning</li>
              </ol>
            </div>
          }
          type="info"
          showIcon
          className="mb-4"
        />
        
        <div className="space-y-6">
          <Row gutter={16}>
            <Col span={8}>
              <Text strong>Religious Tradition:</Text>
              <Select
                className="w-full mt-2"
                value={religiousTradition}
                onChange={(value) => setReligiousTradition(value)}
                disabled={isGenerating}
              >
                {religiousTraditions.map(tradition => (
                  <Option key={tradition.value} value={tradition.value}>{tradition.label}</Option>
                ))}
              </Select>
            </Col>
            <Col span={8}>
              <Text strong>Devotional Category:</Text>
              <Select
                className="w-full mt-2"
                value={devotionalCategory}
                onChange={(value) => setDevotionalCategory(value)}
                disabled={isGenerating}
              >
                {devotionalCategories.map(category => (
                  <Option key={category.value} value={category.value}>{category.label}</Option>
                ))}
              </Select>
            </Col>
            <Col span={8}>
              <Text strong>Spiritual Theme:</Text>
              <Select
                className="w-full mt-2"
                value={devotionalTheme}
                onChange={(value) => setDevotionalTheme(value)}
                disabled={isGenerating}
              >
                {devotionalThemes.map(theme => (
                  <Option key={theme.value} value={theme.value}>{theme.label}</Option>
                ))}
              </Select>
            </Col>
          </Row>

          <div>
            <Text strong>Describe your devotional video:</Text>
            <Input.TextArea
              rows={4}
              value={prompt}
              onChange={(e) => setPrompt(e.target.value)}
              placeholder="Describe the spiritual imagery, setting, or scene you want to visualize..."
              className="mt-2"
              disabled={isGenerating}
            />
            <Text type="secondary" className="block mt-1 text-xs">
              Our AI will enhance your prompt with appropriate religious elements and spiritual symbolism based on your selections
            </Text>
          </div>

          <Row gutter={16}>
            <Col span={8}>
              <Text strong>Video Duration (seconds):</Text>
              <Slider
                min={3}
                max={10}
                onChange={(value) => setDuration(value)}
                value={duration}
                disabled={isGenerating}
                marks={{
                  3: '3s',
                  5: '5s',
                  10: '10s',
                }}
              />
            </Col>
            <Col span={8}>
              <Text strong>Video Quality:</Text>
              <Select
                className="w-full mt-2"
                value={quality}
                onChange={(value) => setQuality(value)}
                disabled={isGenerating}
              >
                <Option value="medium">Medium</Option>
                <Option value="high">High</Option>
              </Select>
            </Col>
            <Col span={8}>
              <Text strong>Visual Style:</Text>
              <Select
                className="w-full mt-2"
                value={style}
                onChange={(value) => setStyle(value)}
                disabled={isGenerating}
              >
                <Option value="cinematic">Cinematic</Option>
                <Option value="artistic">Artistic</Option>
                <Option value="realistic">Realistic</Option>
              </Select>
            </Col>
          </Row>
          
          <div className="mt-6 p-4 border-4 border-indigo-500 rounded-lg bg-gradient-to-r from-indigo-50 to-blue-50 shadow-lg">
            <h3 className="text-center text-xl font-bold text-indigo-800 mb-3">
              ✨ DEVOTIONAL VIDEO GENERATION ✨
            </h3>
            <Button
              type="primary" 
              onClick={handleGenerateVideo}
              disabled={isGenerating || !prompt.trim()}
              style={{ 
                background: 'linear-gradient(90deg, #4f46e5, #3b82f6)',
                borderColor: '#4338ca', 
                fontWeight: 'bold',
                height: '70px',
                fontSize: '20px',
                boxShadow: '0 4px 14px rgba(79, 70, 229, 0.4)'
              }}
              className="w-full"
            >
              {isGenerating ? 
                <><LoadingOutlined /> CREATING YOUR DEVOTIONAL VIDEO...</> : 
                '🕊️ GENERATE DEVOTIONAL VIDEO 🕊️'
              }
            </Button>
            <Text className="block text-center mt-3 text-indigo-700 font-medium">
              Create spiritually meaningful videos for worship, meditation, and religious content
            </Text>
          </div>

          {error && (
            <Alert
              message="Error"
              description={error}
              type="error"
              showIcon
              closable
            />
          )}

          {isGenerating && !videoUrl && (
            <div className="space-y-2">
              <Progress percent={progress} status="active" />
              <Text type="secondary" className="block text-center">{statusMessage}</Text>
              
              {/* Display API call counter and diffusion step information */}
              {diffusionStep && (
                <div className="mt-4 p-3 bg-blue-50 border border-blue-200 rounded">
                  <div className="flex justify-between items-center">
                    <Text strong>Diffusion Progress:</Text> 
                    <Text>{diffusionStep}</Text>
                  </div>
                  <div className="flex justify-between items-center mt-1">
                    <Text strong>API Calls Made:</Text> 
                    <Text>{apiCallCount}</Text>
                  </div>
                  <div className="mt-2">
                    <Text type="secondary">
                      RepeatIt makes network calls for each diffusion step to create your devotional video.
                    </Text>
                  </div>
                </div>
              )}
            </div>
          )}

          {/* Display prompt comparison if available */}
          {showPromptComparison && enhancedPromptDisplay && (
            <div className="mt-4 p-4 bg-gray-50 border border-gray-200 rounded-lg">
              <div className="mb-2">
                <Text strong className="text-indigo-700">Prompt Enhancement</Text>
                <Button 
                  type="text"
                  size="small"
                  className="float-right -mt-1"
                  onClick={() => setShowPromptComparison(!showPromptComparison)}
                >
                  {showPromptComparison ? 'Hide Details' : 'Show Details'}
                </Button>
              </div>
              
              {showPromptComparison && (
                <>
                  <div className="mb-3">
                    <Text type="secondary" className="text-xs">Original Prompt:</Text>
                    <div className="p-2 bg-white border border-gray-200 rounded mt-1">
                      <Text>{originalPrompt}</Text>
                    </div>
                  </div>
                  
                  <div>
                    <Text type="secondary" className="text-xs">
                      {useOpenAI ? 'OpenAI Enhanced Prompt:' : 'Enhanced Prompt:'}
                    </Text>
                    <div className="p-2 bg-white border border-indigo-200 rounded mt-1">
                      <Text className="text-indigo-800">{enhancedPromptDisplay}</Text>
                    </div>
                    <Text type="secondary" className="block mt-1 text-xs">
                      {useOpenAI 
                        ? 'This prompt has been significantly enhanced by OpenAI to create a more accurate and detailed devotional video.' 
                        : 'This prompt has been enhanced with religious elements appropriate to your tradition and theme.'}
                    </Text>
                  </div>
                </>
              )}
            </div>
          )}

          {videoUrl && (
            <div className="mt-6 space-y-4">
              <Title level={4}>Your Devotional Video</Title>
              <div className="border rounded-lg overflow-hidden">
                <video
                  ref={videoRef}
                  controls
                  className="w-full"
                  autoPlay
                  loop
                >
                  <source src={videoUrl} type="video/mp4" />
                  Your browser does not support the video tag.
                </video>
              </div>
              <div className="flex justify-end">
                <Button
                  type="default"
                  icon={<CloudUploadOutlined />}
                  onClick={() => window.open(videoUrl, '_blank')}
                >
                  Download Video
                </Button>
              </div>
            </div>
          )}
        </div>
        <DevotionalHelpModal />
        <OpenAISettingsModal />
      </Card>
    </div>
  );
} 