export interface LogEntry {
  timestamp: string;
  message: string;
  type: 'info' | 'success' | 'error' | 'loading' | 'prompt' | 'parameter';
  data?: any;
}

export interface SubtitleStyle {
  font_size: number;
  font_color: string;
  bg_color: string;
  bg_alpha: number;
}

export interface ConversationPayload {
  topic: string;
  duration_minutes: number;
  segment_duration: number;
  video_size: [number, number];
  subtitle_style: SubtitleStyle;
}

export interface EnhancementResult {
  enhanced: string;
  changes: string[];
} 