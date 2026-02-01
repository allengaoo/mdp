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
  source_id?: string;  // When provided, backend builds context with source object (V1 compatibility)
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
 * Fetch action definitions with optional project filter.
 * 
 * @param projectId - Optional project ID to filter by
 * @returns List of action definitions
 */
export const fetchActions = async (projectId?: string): Promise<IActionDefinitionRead[]> => {
  const params = projectId ? { project_id: projectId } : {};
  const response = await v3Client.get('/ontology/actions', { params });
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
 * Fetch functions with optional project filter.
 * 
 * @param projectId - Optional project ID (Studio context)
 * @returns List of function definitions
 */
export const fetchFunctions = async (projectId?: string): Promise<IFunctionRead[]> => {
  const params = projectId ? { project_id: projectId } : {};
  const response = await v3Client.get('/ontology/functions', { params });
  return response.data || [];
};

/**
 * Create a new function definition.
 */
export const createFunction = async (data: IFunctionCreate): Promise<IFunctionRead> => {
  const response = await v3Client.post('/ontology/functions', data);
  return response.data;
};

/**
 * Get function definition by ID.
 */
export const getFunction = async (functionId: string): Promise<IFunctionRead> => {
  const response = await v3Client.get(`/ontology/functions/${functionId}`);
  return response.data;
};

/**
 * Update an existing function definition.
 */
export const updateFunction = async (
  functionId: string,
  data: Partial<IFunctionCreate>
): Promise<IFunctionRead> => {
  const response = await v3Client.put(`/ontology/functions/${functionId}`, data);
  return response.data;
};

/**
 * Delete a function definition.
 */
export const deleteFunction = async (functionId: string): Promise<void> => {
  await v3Client.delete(`/ontology/functions/${functionId}`);
};

// ==========================================
// Function Definition Types
// ==========================================

export interface IFunctionCreate {
  api_name: string;
  display_name: string;
  description?: string;
  code_content?: string;
  input_params_schema?: Array<{ name: string; type: string; required?: boolean }>;
  output_type?: string;
  bound_object_type_id?: string | null;
  project_id?: string | null;
}

export interface IFunctionRead {
  id: string;
  api_name: string;
  display_name: string;
  description?: string;
  code_content?: string;
  input_params_schema?: Array<{ name: string; type: string; required?: boolean }>;
  output_type: string;
  bound_object_type_id?: string | null;
  project_id?: string | null;
}

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

// ==========================================
// Action Definition CRUD
// ==========================================

/**
 * Validation rule for action definition.
 */
export interface IValidationRule {
  target_field: string;
  expression: string;
  error_message: string;
}

/**
 * Action definition create payload.
 */
export interface IActionDefinitionCreate {
  api_name: string;
  display_name: string;
  description?: string;
  operation_type?: string;
  target_object_type_id?: string;
  link_type_id?: string;
  parameters_schema?: Array<{
    api_id: string;
    display_name: string;
    type: string;
    required?: boolean;
    default_value?: string;
  }>;
  property_mapping?: Record<string, string>;
  validation_rules?: {
    param_validation: IValidationRule[];
    pre_condition: IValidationRule[];
    post_condition: IValidationRule[];
  };
  backing_function_id?: string;
  project_id?: string;
}

/**
 * Action definition read response.
 */
export interface IActionDefinitionRead {
  id: string;
  api_name: string;
  display_name: string;
  description?: string;
  operation_type?: string;
  target_object_type_id?: string;
  link_type_id?: string;
  parameters_schema?: any[];
  property_mapping?: Record<string, string>;
  validation_rules?: {
    param_validation: IValidationRule[];
    pre_condition: IValidationRule[];
    post_condition: IValidationRule[];
  };
  backing_function_id?: string;
  project_id?: string;
}

/**
 * Create a new action definition.
 * 
 * @param data - Action definition create payload
 * @returns Created action definition
 */
export const createActionDefinition = async (
  data: IActionDefinitionCreate
): Promise<IActionDefinitionRead> => {
  const response = await v3Client.post('/ontology/actions', data);
  return response.data;
};

/**
 * Get action definition by ID.
 * 
 * @param actionId - The action ID
 * @returns Action definition
 */
export const getActionDefinition = async (
  actionId: string
): Promise<IActionDefinitionRead> => {
  const response = await v3Client.get(`/ontology/actions/${actionId}`);
  return response.data;
};

/**
 * Update an action definition.
 * 
 * @param actionId - The action ID
 * @param data - Action definition update payload
 * @returns Updated action definition
 */
export const updateActionDefinition = async (
  actionId: string,
  data: Partial<IActionDefinitionCreate>
): Promise<IActionDefinitionRead> => {
  const response = await v3Client.put(`/ontology/actions/${actionId}`, data);
  return response.data;
};

/**
 * Delete an action definition.
 * 
 * @param actionId - The action ID
 */
export const deleteActionDefinition = async (actionId: string): Promise<void> => {
  await v3Client.delete(`/ontology/actions/${actionId}`);
};
