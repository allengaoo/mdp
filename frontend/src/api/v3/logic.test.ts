/**
 * Unit 4: V3 Logic API Client Tests.
 * Tests for createFunction, getFunction, updateFunction, deleteFunction, fetchFunctions.
 */
import { describe, it, expect, vi, beforeEach } from 'vitest';
import v3Client from './client';
import {
  createFunction,
  getFunction,
  updateFunction,
  deleteFunction,
  fetchFunctions,
} from './logic';

vi.mock('./client', () => ({
  default: {
    get: vi.fn(),
    post: vi.fn(),
    put: vi.fn(),
    delete: vi.fn(),
  },
}));

describe('Logic API - Function CRUD', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe('createFunction', () => {
    it('F-A-01: should call POST /ontology/functions with payload', async () => {
      const payload = {
        api_name: 'test_func',
        display_name: 'Test Function',
      };
      const mockRes = { data: { id: 'f1', ...payload, output_type: 'VOID' } };
      vi.mocked(v3Client.post).mockResolvedValueOnce(mockRes as any);

      const result = await createFunction(payload);

      expect(v3Client.post).toHaveBeenCalledWith('/ontology/functions', payload);
      expect(result.id).toBe('f1');
      expect(result.api_name).toBe('test_func');
    });
  });

  describe('getFunction', () => {
    it('F-A-02: should call GET /ontology/functions/{id}', async () => {
      const fid = 'func-123';
      const mockRes = {
        data: { id: fid, api_name: 'get_test', display_name: 'Get Test', output_type: 'STRING' },
      };
      vi.mocked(v3Client.get).mockResolvedValueOnce(mockRes as any);

      const result = await getFunction(fid);

      expect(v3Client.get).toHaveBeenCalledWith(`/ontology/functions/${fid}`);
      expect(result.id).toBe(fid);
    });
  });

  describe('updateFunction', () => {
    it('F-A-03: should call PUT /ontology/functions/{id}', async () => {
      const fid = 'func-456';
      const payload = { display_name: 'Updated Name' };
      const mockRes = {
        data: { id: fid, api_name: 'upd', display_name: 'Updated Name', output_type: 'VOID' },
      };
      vi.mocked(v3Client.put).mockResolvedValueOnce(mockRes as any);

      const result = await updateFunction(fid, payload);

      expect(v3Client.put).toHaveBeenCalledWith(`/ontology/functions/${fid}`, payload);
      expect(result.display_name).toBe('Updated Name');
    });
  });

  describe('deleteFunction', () => {
    it('F-A-04: should call DELETE /ontology/functions/{id}', async () => {
      const fid = 'func-789';
      vi.mocked(v3Client.delete).mockResolvedValueOnce({} as any);

      await deleteFunction(fid);

      expect(v3Client.delete).toHaveBeenCalledWith(`/ontology/functions/${fid}`);
    });
  });

  describe('fetchFunctions', () => {
    it('F-A-05: should call GET without project_id when projectId undefined', async () => {
      const mockRes = { data: [] };
      vi.mocked(v3Client.get).mockResolvedValueOnce(mockRes as any);

      await fetchFunctions();

      expect(v3Client.get).toHaveBeenCalledWith('/ontology/functions', { params: {} });
    });

    it('F-A-06: should call GET with project_id when projectId provided', async () => {
      const mockRes = { data: [] };
      vi.mocked(v3Client.get).mockResolvedValueOnce(mockRes as any);

      await fetchFunctions('proj-1');

      expect(v3Client.get).toHaveBeenCalledWith('/ontology/functions', {
        params: { project_id: 'proj-1' },
      });
    });
  });
});
