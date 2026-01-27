/**
 * V3 Connectors API Functions - MDP Platform V3.1
 * API client for data connection and sync job management.
 */
import v3Client from './client';

// ==========================================
// Connection Types
// ==========================================

export type ConnectorType = 'MYSQL' | 'POSTGRES' | 'S3' | 'KAFKA' | 'REST_API';

export type ConnectorStatus = 'ACTIVE' | 'ERROR' | 'TESTING';

export interface IConnectionConfig {
  host?: string;
  port?: number;
  database?: string;
  user?: string;
  password?: string;
  // S3
  bucket?: string;
  region?: string;
  access_key?: string;
  secret_key?: string;
  // Kafka
  bootstrap_servers?: string;
  // REST API
  base_url?: string;
  auth_type?: string;
  api_key?: string;
  [key: string]: any;
}

export interface IConnectionSummary {
  id: string;
  name: string;
  conn_type: ConnectorType;
  status: ConnectorStatus;
  last_tested_at: string | null;
  created_at: string | null;
}

export interface IConnectionRead {
  id: string;
  name: string;
  conn_type: ConnectorType;
  config_json: IConnectionConfig;
  status: ConnectorStatus;
  error_message: string | null;
  last_tested_at: string | null;
  created_at: string | null;
  updated_at: string | null;
}

export interface IConnectionCreate {
  name: string;
  conn_type: ConnectorType;
  config_json: IConnectionConfig;
}

export interface IConnectionUpdate {
  name?: string;
  conn_type?: ConnectorType;
  config_json?: IConnectionConfig;
}

export interface IConnectionTestRequest {
  conn_type: ConnectorType;
  config_json: IConnectionConfig;
}

export interface IConnectionTestResponse {
  success: boolean;
  message: string;
  latency_ms?: number;
}

// ==========================================
// Source Explorer Types
// ==========================================

export interface ISourceTableInfo {
  name: string;
  schema_name?: string | null;
  columns?: Array<{
    name: string;
    type: string;
    nullable: boolean;
  }> | null;
  row_count?: number | null;
}

export interface ISourceExplorerResponse {
  connection_id: string;
  conn_type: ConnectorType;
  tables: ISourceTableInfo[];
  schemas?: string[] | null;
  error?: string | null;
}

// ==========================================
// Sync Job Types
// ==========================================

export type SyncMode = 'FULL_OVERWRITE' | 'INCREMENTAL';

export type SyncStatus = 'SUCCESS' | 'FAILED' | 'RUNNING';

export interface ISyncJobSourceConfig {
  table?: string;
  schema?: string;
  query?: string;
  [key: string]: any;
}

export interface ISyncJobDef {
  id: string;
  connection_id: string;
  name: string;
  source_config: ISyncJobSourceConfig;
  target_table: string;
  sync_mode: SyncMode;
  schedule_cron: string | null;
  is_enabled: boolean;
  last_run_status: SyncStatus | null;
  last_run_at: string | null;
  rows_synced: number | null;
  created_at: string | null;
  updated_at: string | null;
}

export interface ISyncJobWithConnection extends ISyncJobDef {
  connection_name: string | null;
  connection_type: ConnectorType | null;
}

export interface ISyncJobCreate {
  connection_id: string;
  name: string;
  source_config: ISyncJobSourceConfig;
  target_table: string;
  sync_mode?: SyncMode;
  schedule_cron?: string | null;
  is_enabled?: boolean;
}

export interface ISyncJobUpdate {
  name?: string;
  source_config?: ISyncJobSourceConfig;
  target_table?: string;
  sync_mode?: SyncMode;
  schedule_cron?: string | null;
  is_enabled?: boolean;
}

// ==========================================
// Sync Run Log Types
// ==========================================

export interface ISyncRunLog {
  id: string;
  job_id: string;
  start_time: string;
  end_time: string | null;
  duration_ms: number | null;
  rows_affected: number | null;
  status: SyncStatus;
  message: string | null;
  triggered_by: string;
}

export interface ISyncRunLogWithJob extends ISyncRunLog {
  job_name: string | null;
  connection_name: string | null;
}

// ==========================================
// Connection API Functions
// ==========================================

/**
 * List all connections (summary without sensitive config).
 */
export const fetchConnectors = async (): Promise<IConnectionSummary[]> => {
  const response = await v3Client.get('/connectors');
  return response.data || [];
};

// Alias for backward compatibility
export const fetchConnections = fetchConnectors;

/**
 * Get connection details by ID.
 */
export const fetchConnector = async (id: string): Promise<IConnectionRead> => {
  const response = await v3Client.get(`/connectors/${id}`);
  return response.data;
};

/**
 * Create a new connection.
 */
export const createConnector = async (data: IConnectionCreate): Promise<IConnectionRead> => {
  const response = await v3Client.post('/connectors', data);
  return response.data;
};

/**
 * Update an existing connection.
 */
export const updateConnector = async (id: string, data: IConnectionUpdate): Promise<IConnectionRead> => {
  const response = await v3Client.put(`/connectors/${id}`, data);
  return response.data;
};

/**
 * Delete a connection.
 */
export const deleteConnector = async (id: string): Promise<void> => {
  await v3Client.delete(`/connectors/${id}`);
};

/**
 * Test connection without saving.
 */
export const testConnection = async (data: IConnectionTestRequest): Promise<IConnectionTestResponse> => {
  const response = await v3Client.post('/connectors/test', data);
  return response.data;
};

/**
 * Test existing connection and update its status.
 */
export const testExistingConnection = async (id: string): Promise<IConnectionTestResponse> => {
  const response = await v3Client.post(`/connectors/${id}/test`);
  return response.data;
};

/**
 * Explore source tables/resources.
 */
export const exploreSource = async (id: string): Promise<ISourceExplorerResponse> => {
  const response = await v3Client.get(`/connectors/${id}/explorer`);
  return response.data;
};

// ==========================================
// Sync Job API Functions
// ==========================================

/**
 * List all sync jobs.
 */
export const fetchSyncJobs = async (connectionId?: string): Promise<ISyncJobWithConnection[]> => {
  const params: Record<string, string> = {};
  if (connectionId) {
    params.connection_id = connectionId;
  }
  const response = await v3Client.get('/sync-jobs', { params });
  return response.data || [];
};

/**
 * Get sync job details.
 */
export const fetchSyncJob = async (id: string): Promise<ISyncJobWithConnection> => {
  const response = await v3Client.get(`/sync-jobs/${id}`);
  return response.data;
};

/**
 * Create a new sync job.
 */
export const createSyncJob = async (data: ISyncJobCreate): Promise<ISyncJobDef> => {
  const response = await v3Client.post('/sync-jobs', data);
  return response.data;
};

/**
 * Update an existing sync job.
 */
export const updateSyncJob = async (id: string, data: ISyncJobUpdate): Promise<ISyncJobDef> => {
  const response = await v3Client.put(`/sync-jobs/${id}`, data);
  return response.data;
};

/**
 * Delete a sync job.
 */
export const deleteSyncJob = async (id: string): Promise<void> => {
  await v3Client.delete(`/sync-jobs/${id}`);
};

/**
 * Trigger immediate sync job execution.
 */
export const runSyncJob = async (id: string): Promise<ISyncRunLog> => {
  const response = await v3Client.post(`/sync-jobs/${id}/run`);
  return response.data;
};

/**
 * Get sync job run history.
 */
export const fetchSyncJobLogs = async (jobId: string): Promise<ISyncRunLogWithJob[]> => {
  const response = await v3Client.get(`/sync-jobs/${jobId}/logs`);
  return response.data || [];
};
