/**
 * V3 Chat2App API Client
 * MDP Platform V3.1 - Conversational Intelligence Module
 *
 * Provides natural language query interface with AMIS schema rendering.
 */

import v3Client from './client';

// ==========================================
// Types
// ==========================================

/**
 * Message role in conversation.
 */
export type MessageRole = 'user' | 'assistant' | 'system';

/**
 * Agent response action type.
 */
export type AgentAction =
  | 'query'    // Execute SQL and show results
  | 'form'     // Render AMIS form
  | 'table'    // Render AMIS table
  | 'chart'    // Render AMIS chart
  | 'text'     // Plain text response
  | 'error'    // Error message
  | 'clarify'; // Ask for clarification

/**
 * Single message in conversation.
 */
export interface IChatMessage {
  role: MessageRole;
  content: string;
}

/**
 * AMIS JSON Schema for UI rendering.
 */
export interface IAmisSchema {
  type: string;
  body?: any;
  data?: Record<string, any>;
  [key: string]: any;
}

/**
 * Request to Chat Agent.
 */
export interface IChatRequest {
  message: string;
  context?: Record<string, any>;
  history?: IChatMessage[];
}

/**
 * Response from Chat Agent.
 */
export interface IChatResponse {
  action: AgentAction;
  message: string;
  amis_schema?: IAmisSchema;
  sql?: string;
  data?: Record<string, any>;
  suggestions: string[];
}

/**
 * Chat health check response.
 */
export interface IChatHealthResponse {
  ollama_available: boolean;
  model: string;
  status: string;
}

// ==========================================
// API Functions
// ==========================================

/**
 * Send a message to the Chat Agent.
 *
 * @param request - Chat request with message and optional context/history
 * @returns Chat response with action, message, and optional AMIS schema
 *
 * @example
 * const response = await sendChatMessage({
 *   message: "显示所有海上目标",
 *   context: { currentView: "search" }
 * });
 */
export const sendChatMessage = async (
  request: IChatRequest
): Promise<IChatResponse> => {
  const response = await v3Client.post('/chat/message', request);
  return response.data;
};

/**
 * Check Chat Agent health (Ollama availability).
 *
 * @returns Health status including model availability
 */
export const checkChatHealth = async (): Promise<IChatHealthResponse> => {
  const response = await v3Client.get('/chat/health');
  return response.data;
};

/**
 * Get suggested prompts based on current context.
 *
 * @param context - Current application context (e.g., selected object type)
 * @returns List of suggested prompts
 */
export const getSuggestedPrompts = async (
  context?: Record<string, any>
): Promise<{ prompts: string[] }> => {
  const response = await v3Client.post('/chat/suggestions', { context });
  return response.data;
};

// ==========================================
// Helper Functions
// ==========================================

/**
 * Create a new conversation history array.
 */
export const createConversation = (): IChatMessage[] => [];

/**
 * Add a user message to conversation history.
 */
export const addUserMessage = (
  history: IChatMessage[],
  content: string
): IChatMessage[] => [...history, { role: 'user', content }];

/**
 * Add an assistant message to conversation history.
 */
export const addAssistantMessage = (
  history: IChatMessage[],
  content: string
): IChatMessage[] => [...history, { role: 'assistant', content }];

/**
 * Trim conversation history to last N messages.
 */
export const trimHistory = (
  history: IChatMessage[],
  maxMessages: number = 10
): IChatMessage[] => {
  if (history.length <= maxMessages) {
    return history;
  }
  return history.slice(-maxMessages);
};

/**
 * Check if response has renderable AMIS schema.
 */
export const hasAmisSchema = (response: IChatResponse): boolean => {
  return (
    response.amis_schema !== undefined &&
    response.amis_schema !== null &&
    typeof response.amis_schema.type === 'string'
  );
};

/**
 * Get action display label in Chinese.
 */
export const getActionLabel = (action: AgentAction): string => {
  const labels: Record<AgentAction, string> = {
    query: '查询结果',
    form: '表单',
    table: '数据表',
    chart: '图表',
    text: '文本回复',
    error: '错误',
    clarify: '需要澄清',
  };
  return labels[action] || action;
};
