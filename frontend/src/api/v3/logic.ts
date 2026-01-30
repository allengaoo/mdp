/**
 * V3 Logic API Functions - MDP Platform V3.1
 * API client functions for Actions and Functions management.
 */
import v3Client from './client';

// ==========================================
// Type Definitions
// ==========================================

/**
 * Action definition with resolved function details.
 * Maps to: meta_action_def JOIN meta_function_def
 */
export interface IActionWithFunction {
  id: string;
  api_name: string;
  display_name: string;
  backing_function_id: string;
  // Resolved from FunctionDefinition
  function_api_name: string | null;
  function_display_name: string | null;
}

/**
 * Function definition for list display.
 * Maps to: meta_function_def
 */
export interface IFunctionDef {
  id: string;
  api_name: string;
  display_name: string;
  description: string | null;
  output_type: string;
  code_content: string | null;
}

/**
 * Input parameter schema for dynamic form rendering.
 */
export interface IParamSchema {
  name: string;
  type: 'string' | 'number' | 'boolean';
  required?: boolean;
  default?: any;
  description?: string;
}

/**
 * Action details with input params schema.
 */
export interface IActionDetails {
  id: string;
  api_name: string;
  display_name: string;
  backing_function_id: string;
  function_api_name: string | null;
  function_display_name: string | null;
  input_params_schema: IParamSchema[] | null;
}

/**
 * Request body for action execution.
 */
export interface IActionExecuteRequest {
  params: Record<string, any>;
  project_id?: string;
}

/**
 * Response from action execution.
 */
export interface IActionExecuteResponse {
  success: boolean;
  result: any;
  execution_time_ms: number;
  log_id: string;
  stdout?: string;
  error_message?: string;
}

// ==========================================
// API Functions
// ==========================================

/**
 * Fetch all actions with their bound function details.
 * 
 * @returns List of actions with resolved function names
 */
export const fetchActionsWithFunctions = async (): Promise<IActionWithFunction[]> => {
  const response = await v3Client.get('/ontology/actions/with-functions');
  return response.data || [];
};

/**
 * Fetch all functions for list display.
 * 
 * @returns List of functions with code content for preview
 */
export const fetchFunctionsForList = async (): Promise<IFunctionDef[]> => {
  const response = await v3Client.get('/ontology/functions/for-list');
  return response.data || [];
};

/**
 * Fetch action details including input params schema.
 * 
 * @param actionId - The action ID
 * @returns Action details with input_params_schema for form rendering
 */
export const fetchActionDetails = async (actionId: string): Promise<IActionDetails> => {
  const response = await v3Client.get(`/ontology/actions/${actionId}/details`);
  return response.data;
};

/**
 * Execute an action with given parameters.
 * 
 * @param actionId - The action ID to execute
 * @param request - Execution parameters
 * @returns Execution result with log_id
 */
export const executeAction = async (
  actionId: string,
  request: IActionExecuteRequest
): Promise<IActionExecuteResponse> => {
  const response = await v3Client.post(`/ontology/actions/${actionId}/execute`, request);
  return response.data;
};
