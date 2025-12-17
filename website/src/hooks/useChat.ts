/**
 * useChat hook for chat state management and API calls.
 */

import { useState, useCallback } from 'react';

interface Source {
  chapter: string;
  section: string;
  url: string;
  relevanceScore: number;
  snippet: string;
}

interface Message {
  id: string;
  role: 'user' | 'assistant' | 'system';
  content: string;
  sources?: Source[];
  createdAt: string;
}

interface ChatSession {
  id: string;
  userId?: string;
  startedAt: string;
  contextChapter?: string;
  isActive: boolean;
}

interface UseChatOptions {
  apiUrl?: string;
  contextChapter?: string;
}

interface UseChatReturn {
  messages: Message[];
  isLoading: boolean;
  error: string | null;
  sessionId: string | null;
  sendMessage: (content: string) => Promise<void>;
  askQuestion: (question: string) => Promise<void>;
  createSession: () => Promise<void>;
  clearMessages: () => void;
}

const DEFAULT_API_URL = 'http://localhost:8000/api';

export function useChat(options: UseChatOptions = {}): UseChatReturn {
  const { apiUrl = DEFAULT_API_URL, contextChapter } = options;

  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [sessionId, setSessionId] = useState<string | null>(null);

  const createSession = useCallback(async () => {
    setIsLoading(true);
    setError(null);

    try {
      const response = await fetch(`${apiUrl}/chat/sessions`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          contextChapter,
        }),
      });

      if (!response.ok) {
        throw new Error(`Failed to create session: ${response.status}`);
      }

      const session: ChatSession = await response.json();
      setSessionId(session.id);
      setMessages([]);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to create session');
    } finally {
      setIsLoading(false);
    }
  }, [apiUrl, contextChapter]);

  const sendMessage = useCallback(
    async (content: string) => {
      if (!sessionId) {
        setError('No active session. Please create a session first.');
        return;
      }

      // Add user message immediately
      const userMessage: Message = {
        id: `user-${Date.now()}`,
        role: 'user',
        content,
        createdAt: new Date().toISOString(),
      };
      setMessages(prev => [...prev, userMessage]);

      setIsLoading(true);
      setError(null);

      try {
        const response = await fetch(
          `${apiUrl}/chat/sessions/${sessionId}/messages`,
          {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            },
            body: JSON.stringify({ content }),
          }
        );

        if (!response.ok) {
          throw new Error(`Failed to send message: ${response.status}`);
        }

        const data = await response.json();

        const assistantMessage: Message = {
          id: data.message.id,
          role: 'assistant',
          content: data.message.content,
          sources: data.message.sources,
          createdAt: data.message.createdAt,
        };

        setMessages(prev => [...prev, assistantMessage]);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to send message');
      } finally {
        setIsLoading(false);
      }
    },
    [apiUrl, sessionId]
  );

  const askQuestion = useCallback(
    async (question: string) => {
      // Add user message immediately
      const userMessage: Message = {
        id: `user-${Date.now()}`,
        role: 'user',
        content: question,
        createdAt: new Date().toISOString(),
      };
      setMessages(prev => [...prev, userMessage]);

      setIsLoading(true);
      setError(null);

      try {
        const response = await fetch(`${apiUrl}/chat/ask`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            question,
            contextChapter,
          }),
        });

        if (!response.ok) {
          throw new Error(`Failed to get answer: ${response.status}`);
        }

        const data = await response.json();

        const assistantMessage: Message = {
          id: data.message.id,
          role: 'assistant',
          content: data.message.content,
          sources: data.message.sources,
          createdAt: data.message.createdAt,
        };

        setMessages(prev => [...prev, assistantMessage]);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to get answer');
      } finally {
        setIsLoading(false);
      }
    },
    [apiUrl, contextChapter]
  );

  const clearMessages = useCallback(() => {
    setMessages([]);
    setError(null);
  }, []);

  return {
    messages,
    isLoading,
    error,
    sessionId,
    sendMessage,
    askQuestion,
    createSession,
    clearMessages,
  };
}

export default useChat;
