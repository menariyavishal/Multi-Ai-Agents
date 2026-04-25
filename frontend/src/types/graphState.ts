// Define types matching the backend LangGraph state

export interface AgentCompletion {
  planner: boolean;
  researcher: boolean;
  analyst: boolean;
  writer: boolean;
  reviewer: boolean;
}

export interface ReviewScore {
  score: number;
  feedback: string;
}

export interface GraphState {
  query: string;
  plan?: string;
  research_summary?: string;
  analysis?: any;
  draft?: string;
  review?: ReviewScore;
  final_answer?: string;
  agent_completion: AgentCompletion;
  quality_score: number;
  quality_level: string;
  data_classification: string;
  error?: string;
  status: 'pending' | 'processing' | 'approved' | 'needs_revision' | 'failed' | 'completed';
  iterations_used: number;
  execution_time_seconds: number;
}
