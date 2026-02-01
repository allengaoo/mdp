/**
 * Unit 5: FunctionWizard component tests.
 * MDP Platform V3.1 - Function creation wizard.
 *
 * Note: Full component tests require React deduplication (resolve.dedupe) due to
 * Ant Design/rc-field-form using a separate React instance. Run E2E tests or
 * manual tests to verify UI behavior. API contract is covered by e2e_function_wizard.py.
 */
import React from 'react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, waitFor, act } from '@testing-library/react';
import { createFunction } from '../../api/v3/logic';
import FunctionWizard from './FunctionWizard';

vi.mock('../../api/v3/logic', () => ({
  createFunction: vi.fn(),
}));

vi.mock('../../api/axios', () => ({
  default: {
    post: vi.fn(),
  },
}));

vi.mock('react-router-dom', () => ({
  useParams: vi.fn(() => ({})),
}));


const renderWizard = (props: Partial<React.ComponentProps<typeof FunctionWizard>> = {}) => {
  return render(
    <FunctionWizard
      visible
      onCancel={vi.fn()}
      onSuccess={vi.fn()}
      {...props}
    />
  );
};

describe('FunctionWizard', () => {
  const onCancel = vi.fn();
  const onSuccess = vi.fn();

  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('F-W-00: should export FunctionWizard component', () => {
    expect(FunctionWizard).toBeDefined();
    expect(typeof FunctionWizard).toBe('function');
  });

  describe('Initial render', () => {
    it('F-W-01: should render Step 0 Basic Info when visible', () => {
      renderWizard({ onCancel, onSuccess });
      expect(screen.getByText('Basic Info')).toBeInTheDocument();
      expect(screen.getByPlaceholderText('Function Name')).toBeInTheDocument();
    });

    it('should not render modal content when not visible', () => {
      render(<FunctionWizard visible={false} onCancel={onCancel} onSuccess={onSuccess} />);
      // Modal with visible=false may not render body content in DOM
      expect(screen.queryByPlaceholderText('Function Name')).toBeNull();
    });
  });

  describe('projectId prop', () => {
    it('F-W-02: with projectId should include project_id in payload', async () => {
      vi.mocked(createFunction).mockResolvedValueOnce({
        id: 'func-1',
        api_name: 'test',
        display_name: 'Test',
        output_type: 'VOID',
      } as any);

      renderWizard({ onCancel, onSuccess, projectId: 'proj-1' });

      await act(async () => {
        fireEvent.change(screen.getByPlaceholderText('Function Name'), {
          target: { value: 'Test Function' },
        });
        fireEvent.change(screen.getByPlaceholderText('api_name'), {
          target: { value: 'test_func' },
        });
      });
      await act(async () => {
        await new Promise((r) => setTimeout(r, 50));
      });
      await act(async () => {
        fireEvent.click(screen.getByText('Next'));
      });
      await act(async () => {
        await new Promise((r) => setTimeout(r, 50));
      });
      await act(async () => {
        fireEvent.click(screen.getByText('Next'));
      });
      const createBtn = await screen.findByText('Create');
      fireEvent.click(createBtn);

      await waitFor(() => {
        expect(createFunction).toHaveBeenCalled();
      });

      const callArg = vi.mocked(createFunction).mock.calls[0][0];
      expect(callArg.project_id).toBe('proj-1');
    });

    it('F-W-03: without projectId (OMA) should pass project_id null', async () => {
      vi.mocked(createFunction).mockResolvedValueOnce({
        id: 'func-2',
        api_name: 'oma_func',
        display_name: 'OMA Func',
        output_type: 'VOID',
      } as any);

      renderWizard({ onCancel, onSuccess, projectId: undefined });

      await act(async () => {
        fireEvent.change(screen.getByPlaceholderText('Function Name'), {
          target: { value: 'OMA Func' },
        });
        fireEvent.change(screen.getByPlaceholderText('api_name'), {
          target: { value: 'oma_func' },
        });
      });
      await act(async () => { fireEvent.click(screen.getByText('Next')); });
      await act(async () => { fireEvent.click(screen.getByText('Next')); });
      const createBtn = await screen.findByText('Create');
      fireEvent.click(createBtn);

      await waitFor(() => {
        expect(createFunction).toHaveBeenCalled();
      });

      const callArg = vi.mocked(createFunction).mock.calls[0][0];
      expect(callArg.project_id).toBeNull();
    });
  });

  describe('Step validation', () => {
    it('F-W-04: should require display_name in Step 0', async () => {
      renderWizard({ onCancel, onSuccess });
      fireEvent.click(screen.getByText('Next'));
      await waitFor(() => {
        expect(screen.getByText('Please enter display name')).toBeInTheDocument();
      });
    });
  });

  describe('Create success', () => {
    it('F-W-06: on success should call onSuccess', async () => {
      vi.mocked(createFunction).mockResolvedValueOnce({
        id: 'func-3',
        api_name: 'success_func',
        display_name: 'Success',
        output_type: 'VOID',
      } as any);

      renderWizard({ onCancel, onSuccess });

      await act(async () => {
        fireEvent.change(screen.getByPlaceholderText('Function Name'), {
          target: { value: 'Success' },
        });
        fireEvent.change(screen.getByPlaceholderText('api_name'), {
          target: { value: 'success_func' },
        });
      });
      await act(async () => { fireEvent.click(screen.getByText('Next')); });
      await act(async () => { fireEvent.click(screen.getByText('Next')); });
      const createBtn = await screen.findByText('Create');
      fireEvent.click(createBtn);

      await waitFor(() => {
        expect(onSuccess).toHaveBeenCalled();
      });
    });
  });

  describe('Create failure', () => {
    it('F-W-07: on create failure should not call onSuccess', async () => {
      vi.mocked(createFunction).mockRejectedValueOnce(new Error('Create failed'));

      renderWizard({ onCancel, onSuccess });

      await act(async () => {
        fireEvent.change(screen.getByPlaceholderText('Function Name'), {
          target: { value: 'Fail' },
        });
        fireEvent.change(screen.getByPlaceholderText('api_name'), {
          target: { value: 'fail_func' },
        });
      });
      await act(async () => { fireEvent.click(screen.getByText('Next')); });
      await act(async () => { fireEvent.click(screen.getByText('Next')); });
      const createBtn = await screen.findByText('Create');
      fireEvent.click(createBtn);

      await waitFor(() => {
        expect(createFunction).toHaveBeenCalled();
      });

      expect(onSuccess).not.toHaveBeenCalled();
    });
  });

  describe('Cancel', () => {
    it('should call onCancel when Cancel clicked', () => {
      renderWizard({ onCancel, onSuccess });
      fireEvent.click(screen.getByText('Cancel'));
      expect(onCancel).toHaveBeenCalled();
    });
  });
});
