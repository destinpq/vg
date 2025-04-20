// API client for Video Generator backend

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5001';

/**
 * Generate a long video with the given parameters
 * @param {string} initialPrompt The initial prompt for the video
 * @param {number} totalDuration Total duration in seconds
 * @param {object} options Additional options (segment_duration, fps, width, height, etc)
 * @returns {Promise<object>} The response with job ID and status information
 */
export async function generateLongVideo(initialPrompt, totalDuration, options = {}) {
  const url = new URL(`${API_BASE_URL}/video/generate-long`);
  
  // Add query parameters
  url.searchParams.append('initial_prompt', initialPrompt);
  url.searchParams.append('total_duration', totalDuration);
  
  // Default options
  const defaultOptions = {
    segment_duration: 3,
    fps: 30,
    width: 1280,
    height: 720
  };
  
  // Merge with provided options
  const payload = { ...defaultOptions, ...options };
  
  try {
    const response = await fetch(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(payload),
    });
    
    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail || 'Failed to generate video');
    }
    
    return await response.json();
  } catch (error) {
    console.error('Error generating video:', error);
    throw error;
  }
}

/**
 * Generate a short video with the given parameters
 * @param {string} prompt The prompt for the video
 * @param {number} duration Duration in seconds
 * @param {object} options Additional options (fps, width, height, etc)
 * @returns {Promise<object>} The response with job ID and status information
 */
export async function generateVideo(prompt, duration = 5, options = {}) {
  const url = new URL(`${API_BASE_URL}/video/generate`);
  
  // Add query parameters
  url.searchParams.append('prompt', prompt);
  url.searchParams.append('duration', duration);
  
  // Add other options as query parameters
  Object.entries(options).forEach(([key, value]) => {
    url.searchParams.append(key, value);
  });
  
  try {
    const response = await fetch(url);
    
    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail || 'Failed to generate video');
    }
    
    return await response.json();
  } catch (error) {
    console.error('Error generating video:', error);
    throw error;
  }
}

/**
 * Check the status of a video generation job
 * @param {string} jobId The job ID to check
 * @returns {Promise<object>} The job status information
 */
export async function checkVideoStatus(jobId) {
  const url = `${API_BASE_URL}/video/job-status/${jobId}`;
  
  try {
    const response = await fetch(url);
    
    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail || 'Failed to check video status');
    }
    
    return await response.json();
  } catch (error) {
    console.error('Error checking video status:', error);
    throw error;
  }
}

/**
 * Create an event source for FFmpeg installation progress
 * @returns {EventSource} The event source object
 */
export function createFFmpegInstallEventSource() {
  return new EventSource(`${API_BASE_URL}/video/install-ffmpeg`);
}

/**
 * Get the video URL for a completed job
 * @param {string} jobId The job ID
 * @param {string} filename Optional filename, defaults to generated_video.mp4
 * @returns {string} The URL to the video file
 */
export function getVideoUrl(jobId, filename = 'generated_video.mp4') {
  return `${API_BASE_URL}/output/${jobId}/${filename}`;
}

// Export an object with all API functions
const api = {
  generateLongVideo,
  generateVideo,
  checkVideoStatus,
  createFFmpegInstallEventSource,
  getVideoUrl
};

export default api; 