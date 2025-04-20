// Helper function for API calls
export const apiCall = async (endpoint: string, options = {}) => {
  // Use port 5001 for our backend server
  const baseUrl = 'http://localhost:5001';
  const url = `${baseUrl}${endpoint}`;
  
  console.log(`Making API call to: ${url}`);
  
  const defaultOptions = {
    headers: {
      'Content-Type': 'application/json',
      'Accept': 'application/json',
      'Cache-Control': 'no-cache', // Add cache control headers
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
          // Create a fake Response object with the expected json method
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