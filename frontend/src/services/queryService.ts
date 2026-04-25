import { api } from './api';
import { BaseResponse } from '../types/apiResponses';
import { GraphState } from '../types/graphState';

export interface QueryResponse extends BaseResponse {
  session_id: string;
  conversation_id: string;
  result: GraphState;
}

export interface HistoryListResponse extends BaseResponse {
  conversations: any[];
  total_count: number;
}

export const queryService = {
  /**
   * Submit a new query to the multi-agent system
   */
  submitQuery: async (query: string, user_id: string, max_iterations: number = 3): Promise<QueryResponse> => {
    const response = await api.post<QueryResponse>('/query', {
      query,
      user_id,
      max_iterations
    });
    return response.data;
  },

  /**
   * Get conversation history
   */
  getHistory: async (user_id: string, limit: number = 20, skip: number = 0): Promise<HistoryListResponse> => {
    const response = await api.get<HistoryListResponse>('/history', {
      params: { user_id, limit, skip }
    });
    return response.data;
  }
};
