/**
 * Shared Property Modal component.
 * Reusable modal for both Create and Edit modes.
 */
import React, { useState, useEffect } from 'react';
import {
  Modal,
  Form,
  Input,
  Button,
  Alert,
  Row,
  Col,
  Card,
  InputNumber,
  Space,
  message,
} from 'antd';
import { CheckCircleOutlined, DatabaseOutlined } from '@ant-design/icons';
import apiClient from '../../api/axios';
import { useParams } from 'react-router-dom';

const { TextArea } = Input;

interface SharedPropertyData {
  id?: string;
  display_name: string;
  api_name: string;
  data_type: string;
  formatter?: string | null;
  description?: string | null;
  constraints?: Record<string, any>;
}

interface SharedPropertyModalProps {
  visible: boolean;
  mode: 'create' | 'edit';
  property?: SharedPropertyData | null;
  onCancel: () => void;
  onSuccess: () => void;
}

const PHYSICAL_TYPES = [
  { value: 'STRING', label: 'STRING', icon: '📝' },
  { value: 'INTEGER', label: 'INTEGER', icon: '🔢' },
  { value: 'DOUBLE', label: 'DOUBLE', icon: '📊' },
  { value: 'BOOLEAN', label: 'BOOLEAN', icon: '✓' },
  { value: 'GEOPOINT', label: 'GEOPOINT', icon: '📍' },
  { value: 'DATE', label: 'DATE', icon: '📅' },
];

const SharedPropertyModal: React.FC<SharedPropertyModalProps> = ({
  visible,
  mode,
  property,
  onCancel,
  onSuccess,
}) => {
  const { projectId } = useParams<{ projectId: string }>();
  const [form] = Form.useForm();
  const [selectedType, setSelectedType] = useState<string>('STRING');
  const [loading, setLoading] = useState(false);

  // Initialize form when property changes
  useEffect(() => {
    if (visible) {
      if (mode === 'edit' && property) {
        // Parse constraints from formatter (stored as JSON string)
        let constraints: Record<string, any> = {};
        if (property.formatter) {
          try {
            constraints = JSON.parse(property.formatter);
          } catch (e) {
            // If not JSON, treat as regular formatter
          }
        }
        
        form.setFieldsValue({
          display_name: property.display_name,
          api_name: property.api_name,
          data_type: property.data_type,
          formatter: property.formatter && !constraints.regex_pattern ? property.formatter : '',
          description: property.description || '',
          regex_pattern: constraints.regex_pattern || '',
          min_length: constraints.min_length,
          max_length: constraints.max_length,
          min_value: constraints.min_value,
          max_value: constraints.max_value,
        });
        setSelectedType(property.data_type);
      } else {
        form.resetFields();
        setSelectedType('STRING');
      }
    }
  }, [visible, mode, property, form]);

  // Convert display name to API name
  const convertToApiName = (displayName: string): string => {
    return displayName
      .toLowerCase()
      .replace(/[^a-z0-9]+/g, '_')
      .replace(/^_+|_+$/g, '');
  };

  // Handle display name change to auto-fill API name (only in create mode)
  const handleDisplayNameChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (mode === 'create') {
      const displayName = e.target.value;
      form.setFieldsValue({ api_name: convertToApiName(displayName) });
    }
  };

  // Handle type selection
  const handleTypeSelect = (type: string) => {
    setSelectedType(type);
    form.setFieldsValue({ data_type: type });
    // Clear constraints when type changes
    form.setFieldsValue({
      regex_pattern: '',
      min_length: undefined,
      max_length: undefined,
      min_value: undefined,
      max_value: undefined,
    });
  };

  // Handle submit
  const handleSubmit = async () => {
    try {
      setLoading(true);
      const values = await form.validateFields();

      // Build constraints object based on type
      let constraints: Record<string, any> = {};
      if (selectedType === 'STRING') {
        if (values.regex_pattern) constraints.regex_pattern = values.regex_pattern;
        if (values.min_length !== undefined) constraints.min_length = values.min_length;
        if (values.max_length !== undefined) constraints.max_length = values.max_length;
      } else if (selectedType === 'INTEGER' || selectedType === 'DOUBLE') {
        if (values.min_value !== undefined) constraints.min_value = values.min_value;
        if (values.max_value !== undefined) constraints.max_value = values.max_value;
      }

      // Store constraints as JSON string in formatter field
      const constraintsJson = Object.keys(constraints).length > 0 ? JSON.stringify(constraints) : null;
      const formatterValue = constraintsJson || values.formatter || null;

      if (mode === 'create') {
        const payload = {
          project_id: projectId || '',
          api_name: values.api_name,
          display_name: values.display_name,
          data_type: selectedType,
          formatter: formatterValue,
          description: values.description || null,
        };
        await apiClient.post('/meta/shared-properties', payload);
        message.success('Shared property created successfully');
      } else {
        const payload = {
          display_name: values.display_name,
          data_type: selectedType,
          formatter: formatterValue,
          description: values.description || null,
        };
        await apiClient.put(`/meta/shared-properties/${property?.id}`, payload);
        message.success('Shared property updated successfully');
      }
      onSuccess();
      handleCancel();
    } catch (error: any) {
      if (error.errorFields) {
        // Form validation errors
        return;
      }
      message.error(error.response?.data?.detail || `Failed to ${mode} shared property`);
    } finally {
      setLoading(false);
    }
  };

  // Handle cancel
  const handleCancel = () => {
    form.resetFields();
    setSelectedType('STRING');
    onCancel();
  };

  const isStringType = selectedType === 'STRING';
  const isNumericType = selectedType === 'INTEGER' || selectedType === 'DOUBLE';
  const hasConstraints = isStringType || isNumericType;

  return (
    <Modal
      title={mode === 'create' ? 'Create Standard Property' : 'Edit Standard Property'}
      open={visible}
      onCancel={handleCancel}
      width={800}
      footer={[
        <Button key="cancel" onClick={handleCancel}>
          Cancel
        </Button>,
        <Button key="submit" type="primary" loading={loading} onClick={handleSubmit}>
          {mode === 'create' ? 'Create' : 'Save'}
        </Button>,
      ]}
      destroyOnClose
    >
      <Form form={form} layout="vertical">
        {/* Top Info Alert */}
        <Alert
          type="warning"
          message="标准属性库 (SPT)"
          description="标准属性库 (SPT) 定义了本体世界的逻辑规范，为不同对象类型提供统一的属性定义标准。"
          showIcon
          style={{ marginBottom: 24 }}
        />

        {/* Row 1: Basic Info (2 Columns) */}
        <Row gutter={16}>
          <Col span={12}>
            <Form.Item
              name="display_name"
              label="Semantic Name"
              rules={[{ required: true, message: 'Please enter semantic name' }]}
            >
              <Input
                placeholder="e.g., Location Latitude"
                onChange={handleDisplayNameChange}
                disabled={mode === 'edit'}
              />
            </Form.Item>
          </Col>
          <Col span={12}>
            <Form.Item
              name="api_name"
              label="API Identifier"
              rules={[{ required: true, message: 'Please enter API identifier' }]}
            >
              <Input placeholder="e.g., location_lat" disabled={mode === 'edit'} />
            </Form.Item>
          </Col>
        </Row>

        {/* Row 2: Physical Type Selector (Card Grid) */}
        <Form.Item
          name="data_type"
          label={
            <Space>
              <DatabaseOutlined />
              <span>预物理类型 (Expected Physical Type)</span>
            </Space>
          }
          rules={[{ required: true, message: 'Please select physical type' }]}
        >
          <Row gutter={[16, 16]}>
            {PHYSICAL_TYPES.map((type) => {
              const isSelected = selectedType === type.value;
              return (
                <Col span={8} key={type.value}>
                  <Card
                    hoverable
                    onClick={() => handleTypeSelect(type.value)}
                    style={{
                      border: isSelected ? '2px solid #1890ff' : '1px solid #d9d9d9',
                      backgroundColor: isSelected ? '#e6f7ff' : '#fff',
                      cursor: 'pointer',
                      textAlign: 'center',
                      height: '100%',
                      position: 'relative',
                    }}
                    styles={{ body: { padding: '16px' } }}
                  >
                    {isSelected && (
                      <CheckCircleOutlined
                        style={{
                          position: 'absolute',
                          top: 8,
                          right: 8,
                          color: '#1890ff',
                          fontSize: 18,
                        }}
                      />
                    )}
                    <div style={{ fontSize: 24, marginBottom: 8 }}>{type.icon}</div>
                    <div style={{ fontWeight: isSelected ? 600 : 400 }}>{type.label}</div>
                  </Card>
                </Col>
              );
            })}
          </Row>
        </Form.Item>

        {/* Row 3: Field Constraints (Dynamic Section) */}
        <Form.Item label="Field Constraints">
          <div
            style={{
              background: '#fafafa',
              border: '1px solid #d9d9d9',
              padding: '16px',
              borderRadius: 4,
              opacity: hasConstraints ? 1 : 0.5,
              pointerEvents: hasConstraints ? 'auto' : 'none',
            }}
          >
            {!hasConstraints && (
              <div style={{ color: '#8c8c8c', textAlign: 'center' }}>
                No constraints available for this type
              </div>
            )}

            {isStringType && (
              <Row gutter={16}>
                <Col span={24}>
                  <Form.Item name="regex_pattern" label="Regex Pattern">
                    <Input placeholder="^[A-Z0-9]+$" />
                  </Form.Item>
                </Col>
                <Col span={12}>
                  <Form.Item name="min_length" label="Min Length">
                    <InputNumber
                      style={{ width: '100%' }}
                      min={0}
                      placeholder="Min length"
                    />
                  </Form.Item>
                </Col>
                <Col span={12}>
                  <Form.Item name="max_length" label="Max Length">
                    <InputNumber
                      style={{ width: '100%' }}
                      min={0}
                      placeholder="Max length"
                    />
                  </Form.Item>
                </Col>
              </Row>
            )}

            {isNumericType && (
              <Row gutter={16}>
                <Col span={12}>
                  <Form.Item name="min_value" label="Min Value">
                    <InputNumber
                      style={{ width: '100%' }}
                      placeholder="Min value"
                    />
                  </Form.Item>
                </Col>
                <Col span={12}>
                  <Form.Item name="max_value" label="Max Value">
                    <InputNumber
                      style={{ width: '100%' }}
                      placeholder="Max value"
                    />
                  </Form.Item>
                </Col>
              </Row>
            )}
          </div>
        </Form.Item>

        {/* Row 4: Description */}
        <Form.Item name="description" label="Description">
          <TextArea rows={4} placeholder="Enter description..." />
        </Form.Item>
      </Form>
    </Modal>
  );
};

export default SharedPropertyModal;

