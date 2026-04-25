import { useState, useEffect } from 'react';
import { GraphState } from '../types/graphState';

export interface StreamEvent {
  node: string;
  state?: Partial<GraphState>;
  message?: string;
  error?: string;
}

export function useAgentStream(sessionId: string | null) {
  const [activeNode, setActiveNode] = useState<string | null>(null);
  const [streamData, setStreamData] = useState<StreamEvent[]>([]);
  const [isStreaming, setIsStreaming] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!sessionId) {
      setActiveNode(null);
      setStreamData([]);
      setIsStreaming(false);
      return;
    }

    setIsStreaming(true);
    setError(null);
    setStreamData([]);

    // Get API key since we might need to pass it in query params if headers 
    // aren't fully supported by EventSource in all browsers for cross-origin
    // though the proxy will help. Let's assume proxy works properly.
    const eventSource = new EventSource(`/api/v1/stream?session_id=${sessionId}`);

    eventSource.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data) as StreamEvent;
        
        if (data.node) {
          setActiveNode(data.node);
        }
        
        setStreamData((prev) => [...prev, data]);
        
        // If finished, close cleanly
        if (data.node === 'end' || data.node === '__end__') {
          setIsStreaming(false);
          setActiveNode(null); // Clear active node glow
          eventSource.close();
        }
      } catch (err) {
        console.error("Failed to parse stream event", err);
      }
    };

    eventSource.onerror = (err) => {
      console.error("EventSource error:", err);
      setError("Stream connection failed or was closed.");
      setIsStreaming(false);
      eventSource.close();
    };

    return () => {
      if (eventSource.readyState !== EventSource.CLOSED) {
        eventSource.close();
      }
    };
  }, [sessionId]);

  return {
    activeNode,
    streamData,
    isStreaming,
    error
  };
}
