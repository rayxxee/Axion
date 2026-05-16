import { useState, useEffect, useRef } from 'react';

/**
 * Custom hook for Server-Sent Events.
 * Connects to an SSE endpoint and returns events, completion status, and errors.
 */
export function useSSE(jobId) {
  const [events, setEvents] = useState([]);
  const [isComplete, setIsComplete] = useState(false);
  const [error, setError] = useState(null);
  const eventSourceRef = useRef(null);

  useEffect(() => {
    if (!jobId) return;

    const baseUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000';
    const url = `${baseUrl}/api/v1/analyze/${jobId}/stream`;
    const es = new EventSource(url);
    eventSourceRef.current = es;

    es.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        setEvents((prev) => [...prev, data]);

        if (data.event === 'pipeline_done') {
          setIsComplete(true);
          es.close();
        }

        if (data.event === 'error') {
          setError(data.data?.message || 'Pipeline error');
          es.close();
        }
      } catch (err) {
        console.error('SSE parse error:', err);
      }
    };

    es.onerror = () => {
      setError('Connection lost');
      es.close();
    };

    return () => {
      es.close();
    };
  }, [jobId]);

  return { events, isComplete, error };
}
