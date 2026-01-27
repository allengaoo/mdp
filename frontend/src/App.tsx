import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import MainLayout from './layouts/MainLayout';
import OntologyLibrary from './platform/OMA/OntologyLibrary';
import ObjectCenter from './platform/OMA/ObjectCenter';
import RelationGraph from './platform/OMA/RelationGraph';
import ActionLogic from './platform/OMA/ActionLogic';
// DataLink components
import ConnectorList from './platform/DataLink/ConnectorList';
import ConnectorWizard from './platform/DataLink/ConnectorWizard';
import ConnectorDetail from './platform/DataLink/ConnectorDetail';
import { MappingEditor } from './platform/DataLink/MultimodalMapping';
import { IndexHealthPage } from './platform/DataLink/IndexHealth';
// Explorer components
import { GlobalSearchPage } from './platform/Explorer';
import { GraphAnalysisPage } from './platform/Explorer/GraphAnalysis';
import { Object360Page } from './platform/Explorer/Object360';
import { Chat2AppPage } from './platform/Explorer/Chat2App';
import StudioLayout from './platform/Studio/StudioLayout';
import TopologyView from './platform/Studio/TopologyView';
import ObjectTypeList from './platform/Studio/ObjectTypeList';
import LinkTypeList from './platform/Studio/LinkTypeList';
import SharedPropertyList from './platform/Studio/SharedPropertyList';
import PhysicalPropertyList from './platform/Studio/PhysicalPropertyList';
import ActionDefinitionList from './platform/Studio/ActionDefinitionList';
import FunctionList from './platform/Studio/FunctionList';
import ExecutionLogList from './platform/Studio/ExecutionLogList';
import OntologyTest from './platform/Studio/OntologyTest';
// Global components
import GlobalSharedPropertyList from './platform/Registry/GlobalSharedPropertyList';
// Common components
import UnderConstruction from './components/common/UnderConstruction';
import 'antd/dist/reset.css';
import './App.css';

function App() {
  return (
    <BrowserRouter
      future={{
        v7_startTransition: true,
      }}
    >
      <Routes>
        <Route path="/" element={<MainLayout />}>
          <Route index element={<Navigate to="/oma/library" replace />} />
          
          {/* ========== 构建与定义 ========== */}
          {/* 本体管理 */}
          <Route path="oma/library" element={<OntologyLibrary />} />
          <Route path="oma/objects" element={<ObjectCenter />} />
          <Route path="oma/shared-properties" element={<GlobalSharedPropertyList />} />
          <Route path="oma/relations" element={<RelationGraph />} />
          <Route path="oma/actions" element={<ActionLogic />} />
          
          {/* 数据链接 */}
          <Route path="data/connectors" element={<ConnectorList />} />
          <Route path="data/connectors/new" element={<ConnectorWizard />} />
          <Route path="data/connectors/:id" element={<ConnectorDetail />} />
          <Route path="data/connectors/:id/edit" element={<ConnectorWizard />} />
          <Route path="data/mapping" element={<MappingEditor />} />
          <Route path="data/health" element={<IndexHealthPage />} />
          
          {/* ========== 探索与分析 ========== */}
          {/* 洞察与分析 */}
          <Route path="explore/search" element={<GlobalSearchPage />} />
          <Route path="explore/graph" element={<GraphAnalysisPage />} />
          <Route path="explore/media" element={<UnderConstruction title="媒体视图" />} />
          <Route path="explore/object360" element={<Object360Page />} />
          <Route path="explore/object/:objectId" element={<Object360Page />} />
          <Route path="explore/spacetime" element={<UnderConstruction title="时空分析" />} />
          <Route path="explore/chat" element={<Chat2AppPage />} />
          
          {/* ========== 系统管理 ========== */}
          {/* 控制中心 */}
          <Route path="system/permissions" element={<UnderConstruction title="权限策略" />} />
          <Route path="system/approval" element={<UnderConstruction title="变更审批" />} />
          <Route path="system/quota" element={<UnderConstruction title="资源配额" />} />
        </Route>
        <Route path="/oma/project/:projectId" element={<StudioLayout />}>
          <Route index element={<Navigate to="topology" replace />} />
          <Route path="topology" element={<TopologyView />} />
          <Route path="object-types" element={<ObjectTypeList />} />
          <Route path="link-types" element={<LinkTypeList />} />
          <Route path="shared-properties" element={<SharedPropertyList />} />
          <Route path="physical-properties" element={<PhysicalPropertyList />} />
          <Route path="actions" element={<ActionDefinitionList />} />
          <Route path="functions" element={<FunctionList />} />
          <Route path="logs" element={<ExecutionLogList />} />
          <Route path="test" element={<OntologyTest />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}

export default App;
