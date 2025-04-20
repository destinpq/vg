import React, { useState, useEffect, useRef } from 'react';

const FFmpegInstaller = () => {
  const [logs, setLogs] = useState([]);
  const [installing, setInstalling] = useState(false);
  const [installed, setInstalled] = useState(false);
  const [error, setError] = useState(null);
  const [progress, setProgress] = useState(0);
  const eventSourceRef = useRef(null);
  const logsEndRef = useRef(null);

  // Auto-scroll to the bottom of logs when new logs arrive
  useEffect(() => {
    if (logsEndRef.current) {
      logsEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [logs]);

  // Clean up event source on unmount
  useEffect(() => {
    return () => {
      if (eventSourceRef.current) {
        eventSourceRef.current.close();
      }
    };
  }, []);

  const installFFmpeg = async () => {
    // Reset state
    setLogs([]);
    setInstalled(false);
    setError(null);
    setProgress(0);
    setInstalling(true);

    try {
      // Close any existing connection
      if (eventSourceRef.current) {
        eventSourceRef.current.close();
      }

      // Create a new event source connection
      const eventSource = new EventSource('http://localhost:5001/video/install-ffmpeg');
      eventSourceRef.current = eventSource;

      // Handle incoming events
      eventSource.onmessage = (event) => {
        const data = JSON.parse(event.data);
        console.log('Received event:', data);

        switch (data.type) {
          case 'log':
            setLogs(prevLogs => [...prevLogs, data.data]);
            break;
          case 'progress':
            setProgress(data.data.percent);
            break;
          case 'result':
            if (data.data.status === 'success') {
              setInstalled(true);
              addLog('success', `FFmpeg ${data.data.already_installed ? 'was already installed' : 'has been successfully installed'}`);
            } else {
              setError(data.data.message);
              addLog('error', data.data.message);
            }
            // Close the connection when we get a result
            eventSource.close();
            eventSourceRef.current = null;
            break;
          default:
            console.log('Unknown event type:', data.type);
        }
      };

      // Handle errors
      eventSource.onerror = (err) => {
        console.error('EventSource error:', err);
        setError('Connection error. Please try again.');
        addLog('error', 'Connection to server lost. Please try again.');
        eventSource.close();
        eventSourceRef.current = null;
        setInstalling(false);
      };
    } catch (err) {
      console.error('Error setting up event source:', err);
      setError(err.message);
      setInstalling(false);
    }
  };

  // Helper function to add a log entry
  const addLog = (level, message) => {
    setLogs(prevLogs => [...prevLogs, { level, message }]);
  };

  // Function to get appropriate color for log level
  const getLogColor = (level) => {
    switch (level) {
      case 'error': return 'text-red-500';
      case 'warning': return 'text-yellow-500';
      case 'success': return 'text-green-500';
      case 'info':
      default: return 'text-blue-500';
    }
  };

  return (
    <div className="bg-white shadow-md rounded-lg p-6">
      <h2 className="text-xl font-bold mb-4">FFmpeg Installation</h2>
      
      {!installing && !installed && (
        <button
          onClick={installFFmpeg}
          className="bg-blue-500 hover:bg-blue-600 text-white font-bold py-2 px-4 rounded focus:outline-none focus:shadow-outline"
        >
          Install FFmpeg
        </button>
      )}

      {installing && (
        <div className="mb-4">
          <div className="flex justify-between mb-1">
            <span>Installing FFmpeg...</span>
            <span>{progress}%</span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-2.5">
            <div
              className="bg-blue-500 h-2.5 rounded-full"
              style={{ width: `${progress}%` }}
            ></div>
          </div>
        </div>
      )}

      {installed && (
        <div className="bg-green-100 border-l-4 border-green-500 text-green-700 p-4 mb-4">
          <p className="font-bold">FFmpeg is installed and ready to use!</p>
        </div>
      )}

      {error && (
        <div className="bg-red-100 border-l-4 border-red-500 text-red-700 p-4 mb-4">
          <p className="font-bold">Installation Error</p>
          <p>{error}</p>
        </div>
      )}

      {logs.length > 0 && (
        <div className="mt-4">
          <h3 className="font-semibold mb-2">Installation Logs</h3>
          <div className="bg-gray-800 text-white p-4 rounded-md h-64 overflow-y-auto">
            {logs.map((log, index) => (
              <div key={index} className="mb-1">
                <span className={getLogColor(log.level)}>
                  [{log.level.toUpperCase()}]
                </span>{' '}
                {log.message}
              </div>
            ))}
            <div ref={logsEndRef} />
          </div>
        </div>
      )}
    </div>
  );
};

export default FFmpegInstaller; 