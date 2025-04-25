export interface LogEntry {
  timestamp: string;
  message: string;
  type: 'info' | 'success' | 'error' | 'loading' | 'prompt' | 'parameter';
  data?: any;
}

// Video generation stages with their percentage thresholds
export const generationStages = [
  { title: 'Initializing', icon: 'setting', threshold: 15 },
  { title: 'Loading Model', icon: 'cloud-download', threshold: 20 },
  { title: 'Processing Prompt', icon: 'code', threshold: 25 },
  { title: 'Generating Latents', icon: 'rocket', threshold: 30 },
  { title: 'Diffusion Steps', icon: 'experiment', threshold: 90 },
  { title: 'Rendering Frames', icon: 'file-image', threshold: 95 },
  { title: 'Finalizing Video', icon: 'video-camera', threshold: 100 }
]; 