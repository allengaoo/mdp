import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import MainLayout from './layouts/MainLayout';
import OntologyLibrary from './platform/OMA/OntologyLibrary';
import BattlefieldDashboard from './apps/Battlefield/Dashboard';
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
          <Route path="oma/library" element={<OntologyLibrary />} />
          <Route path="apps/battlefield" element={<BattlefieldDashboard />} />
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
