/**
 * GlobalSearchPage Component
 * MDP Platform - Global Search Module (Object Explorer)
 * 
 * A "Palantir Object Explorer" style search experience with:
 * - Large centered search bar with image upload
 * - Left sidebar with dynamic facets
 * - Main grid with search results
 */

import React, { useState, useCallback, useEffect } from 'react';
import {
  Input,
  Button,
  Space,
  Spin,
  Empty,
  Alert,
  Pagination,
  Typography,
  Tooltip,
  Upload,
  message,
  Row,
  Col,
  Card,
  Divider,
  Tag,
} from 'antd';
import {
  SearchOutlined,
  CameraOutlined,
  ClearOutlined,
  ReloadOutlined,
  FilterOutlined,
} from '@ant-design/icons';
import type { UploadFile } from 'antd/es/upload/interface';
import {
  searchObjects,
  getSearchFacets,
  buildFiltersFromSelections,
  IObjectSearchResponse,
  IFacet,
  IObjectHit,
} from '../../api/v3/search';
import FacetGroup from './FacetGroup';
import SearchResultCard from './SearchResultCard';

const { Title, Text } = Typography;

const GlobalSearchPage: React.FC = () => {
  // Search state
  const [searchText, setSearchText] = useState('');
  const [vectorEmbedding, setVectorEmbedding] = useState<number[] | undefined>();
  const [facetSelections, setFacetSelections] = useState<Record<string, string[]>>({});
  const [page, setPage] = useState(1);
  const [pageSize] = useState(20);

  // Results state
  const [searchResponse, setSearchResponse] = useState<IObjectSearchResponse | null>(null);
  const [facets, setFacets] = useState<IFacet[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Image upload state
  const [uploadedImage, setUploadedImage] = useState<UploadFile | null>(null);
  const [imageProcessing, setImageProcessing] = useState(false);

  // Execute search
  const doSearch = useCallback(async () => {
    if (!searchText && !vectorEmbedding && Object.keys(facetSelections).length === 0) {
      // Load initial facets even without search
      try {
        const facetResponse = await getSearchFacets();
        setFacets(facetResponse.facets);
      } catch (err) {
        console.error('Failed to load facets:', err);
      }
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const filters = buildFiltersFromSelections(facetSelections);

      const response = await searchObjects({
        query_text: searchText || undefined,
        query_vector: vectorEmbedding,
        filters: Object.keys(filters).length > 0 ? filters : undefined,
        page,
        page_size: pageSize,
      });

      setSearchResponse(response);
      
      // Update facets from response
      if (response.facets && response.facets.length > 0) {
        setFacets(response.facets);
      }
    } catch (err: any) {
      const errorMsg = err.response?.data?.detail || '搜索失败，请重试';
      setError(errorMsg);
      message.error(errorMsg);
    } finally {
      setLoading(false);
    }
  }, [searchText, vectorEmbedding, facetSelections, page, pageSize]);

  // Initial load - get facets
  useEffect(() => {
    const loadInitialFacets = async () => {
      try {
        const facetResponse = await getSearchFacets();
        setFacets(facetResponse.facets);
      } catch (err) {
        console.error('Failed to load initial facets:', err);
      }
    };
    loadInitialFacets();
  }, []);

  // Search when dependencies change
  useEffect(() => {
    doSearch();
  }, [facetSelections, page]);

  // Handle search submit
  const handleSearch = () => {
    setPage(1);
    doSearch();
  };

  // Handle Enter key
  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      handleSearch();
    }
  };

  // Handle facet change
  const handleFacetChange = (field: string, values: string[]) => {
    setFacetSelections(prev => ({
      ...prev,
      [field]: values,
    }));
    setPage(1);
  };

  // Clear all filters
  const handleClearFilters = () => {
    setFacetSelections({});
    setSearchText('');
    setVectorEmbedding(undefined);
    setUploadedImage(null);
    setPage(1);
  };

  // Handle image upload (mock vector generation)
  const handleImageUpload = async (file: UploadFile) => {
    setImageProcessing(true);
    setUploadedImage(file);

    try {
      // Mock: Generate random 768-dim vector
      // In production, call an embedding API
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      const mockVector = Array.from({ length: 768 }, () => Math.random() * 2 - 1);
      setVectorEmbedding(mockVector);
      
      message.success('图片已上传，正在进行语义搜索...');
      setPage(1);
      doSearch();
    } catch (err) {
      message.error('图片处理失败');
    } finally {
      setImageProcessing(false);
    }

    return false; // Prevent default upload
  };

  // Remove uploaded image
  const handleRemoveImage = () => {
    setUploadedImage(null);
    setVectorEmbedding(undefined);
  };

  // Count active filters
  const activeFilterCount = Object.values(facetSelections).reduce(
    (acc, arr) => acc + arr.length,
    0
  );

  // Handle result click
  const handleResultClick = (hit: IObjectHit) => {
    message.info(`点击了对象: ${hit.display_name} (${hit.id})`);
    // TODO: Navigate to object detail page
  };

  return (
    <div style={{ padding: 24, minHeight: '100vh', background: '#f5f5f5' }}>
      {/* Header with Search Bar */}
      <div
        style={{
          textAlign: 'center',
          marginBottom: 32,
          padding: '24px 0',
          background: '#fff',
          borderRadius: 12,
          boxShadow: '0 2px 8px rgba(0,0,0,0.06)',
        }}
      >
        <Title level={2} style={{ marginBottom: 8 }}>
          全局搜索 (Object Explorer)
        </Title>
        <Text type="secondary" style={{ display: 'block', marginBottom: 24 }}>
          搜索所有对象类型，支持关键词和图片语义搜索
        </Text>

        {/* Search Bar */}
        <div style={{ maxWidth: 800, margin: '0 auto', padding: '0 24px' }}>
          <Space.Compact style={{ width: '100%' }}>
            <Input
              size="large"
              placeholder="输入关键词搜索对象..."
              value={searchText}
              onChange={(e) => setSearchText(e.target.value)}
              onKeyPress={handleKeyPress}
              prefix={<SearchOutlined style={{ color: '#bfbfbf' }} />}
              suffix={
                <Upload
                  accept="image/*"
                  showUploadList={false}
                  beforeUpload={handleImageUpload}
                >
                  <Tooltip title="上传图片进行语义搜索">
                    <Button
                      type="text"
                      icon={<CameraOutlined />}
                      loading={imageProcessing}
                    />
                  </Tooltip>
                </Upload>
              }
              style={{ borderRadius: '8px 0 0 8px' }}
            />
            <Button
              type="primary"
              size="large"
              icon={<SearchOutlined />}
              onClick={handleSearch}
              loading={loading}
              style={{ borderRadius: '0 8px 8px 0' }}
            >
              搜索
            </Button>
          </Space.Compact>

          {/* Uploaded Image Preview */}
          {uploadedImage && (
            <div style={{ marginTop: 12, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
              <Tag 
                closable 
                onClose={handleRemoveImage}
                color="blue"
              >
                <CameraOutlined /> 图片语义搜索已启用
              </Tag>
            </div>
          )}
        </div>
      </div>

      {/* Main Content: Facets + Results */}
      <Row gutter={24}>
        {/* Left Sidebar: Facets */}
        <Col xs={24} md={6}>
          <Card
            title={
              <Space>
                <FilterOutlined />
                <span>筛选条件</span>
                {activeFilterCount > 0 && (
                  <Tag color="blue">{activeFilterCount}</Tag>
                )}
              </Space>
            }
            extra={
              activeFilterCount > 0 && (
                <Button
                  type="link"
                  size="small"
                  icon={<ClearOutlined />}
                  onClick={handleClearFilters}
                >
                  清除
                </Button>
              )
            }
            style={{ borderRadius: 8 }}
            styles={{ body: { padding: 12 } }}
          >
            {facets.length === 0 ? (
              <Empty description="暂无筛选条件" image={Empty.PRESENTED_IMAGE_SIMPLE} />
            ) : (
              facets.map((facet) => (
                <FacetGroup
                  key={facet.field}
                  facet={facet}
                  selectedValues={facetSelections[facet.field] || []}
                  onChange={handleFacetChange}
                />
              ))
            )}
          </Card>
        </Col>

        {/* Right Main: Results */}
        <Col xs={24} md={18}>
          {/* Results Header */}
          <Card
            style={{ marginBottom: 16, borderRadius: 8 }}
            styles={{ body: { padding: '12px 16px' } }}
          >
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <Space>
                {searchResponse && (
                  <Text>
                    找到 <Text strong>{searchResponse.total}</Text> 个结果
                    {searchResponse.query && (
                      <Text type="secondary"> (搜索: "{searchResponse.query}")</Text>
                    )}
                  </Text>
                )}
              </Space>
              <Button
                icon={<ReloadOutlined />}
                onClick={doSearch}
                loading={loading}
              >
                刷新
              </Button>
            </div>
          </Card>

          {/* Error Alert */}
          {error && (
            <Alert
              message="搜索出错"
              description={error}
              type="error"
              showIcon
              closable
              style={{ marginBottom: 16 }}
              onClose={() => setError(null)}
            />
          )}

          {/* Loading State */}
          {loading && (
            <div style={{ textAlign: 'center', padding: 60 }}>
              <Spin size="large" tip="搜索中..." />
            </div>
          )}

          {/* Results Grid */}
          {!loading && searchResponse && searchResponse.hits.length > 0 && (
            <>
              <div>
                {searchResponse.hits.map((hit) => (
                  <SearchResultCard
                    key={hit.id}
                    hit={hit}
                    onClick={handleResultClick}
                  />
                ))}
              </div>

              {/* Pagination */}
              <div style={{ textAlign: 'center', marginTop: 24 }}>
                <Pagination
                  current={page}
                  pageSize={pageSize}
                  total={searchResponse.total}
                  onChange={(p) => setPage(p)}
                  showSizeChanger={false}
                  showTotal={(total) => `共 ${total} 条`}
                />
              </div>
            </>
          )}

          {/* Empty State */}
          {!loading && (!searchResponse || searchResponse.hits.length === 0) && (
            <Card style={{ borderRadius: 8 }}>
              <Empty
                description={
                  searchText || vectorEmbedding
                    ? '未找到匹配的对象'
                    : '输入关键词或上传图片开始搜索'
                }
              >
                {(searchText || vectorEmbedding) && (
                  <Button type="primary" onClick={handleClearFilters}>
                    清除搜索条件
                  </Button>
                )}
              </Empty>
            </Card>
          )}
        </Col>
      </Row>
    </div>
  );
};

export default GlobalSearchPage;
