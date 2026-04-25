import { useState, useCallback } from 'react';
import { queryService } from '../services/queryService';
import { useAuth } from './useAuth';
import { GraphState } from '../types/graphState';

export function useQuery() {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [result, setResult] = useState<GraphState | null>(null);
  
  const { user } = useAuth();

  const submitQuery = useCallback(async (query: string) => {
    if (!user?.userId) {
      setError("You must be logged in to submit a query");
      return null;
    }

    setIsLoading(true);
    setError(null);
    setSessionId(null);
    setResult(null);

    try {
      // Backend returns initial response with session_id
      const data = await queryService.submitQuery(query, user.userId);
      if (data.status === 'success') {
        setSessionId(data.session_id);
        setResult(data.result);
        return data.session_id;
      } else {
        setError(data.error || "Failed to process query");
        return null;
      }
    } catch (err: any) {
      console.error("Query Error:", err);
      // Wait, let's fix the type: error could be generic Error or AxiosError
      // using any for now but should be more specific
      setError(err.response?.data?.error || err.message || "An unexpected error occurred");
      return null;
    } finally {
      setIsLoading(false);
    }
  }, [user]);

  const clearQuery = useCallback(() => {
    setResult(null);
    setSessionId(null);
    setError(null);
  }, []);

  return {
    isLoading,
    error,
    sessionId,
    result,
    submitQuery,
    clearQuery
  };
}
