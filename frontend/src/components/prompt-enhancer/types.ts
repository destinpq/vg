export interface PromptEnhancerProps {
  initialPrompt: string;
  onPromptChange: (prompt: string) => void;
  enhancePrompt?: (prompt: string) => Promise<{enhanced: string, changes?: string[]}>;
  enhanceEnabled?: boolean;
  onEnableChange?: (enabled: boolean) => void;
  suggestions?: string[];
  loading?: boolean;
  placeholder?: string;
  className?: string;
}

export interface EnhancementResult {
  enhanced: string;
  changes?: string[];
} 