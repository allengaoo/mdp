/**
 * Battlefield Cockpit Dashboard component.
 * Pure frontend with mock data - displays fighters and targets on an interactive map.
 */
import React from 'react';
import { MapContainer, TileLayer, Marker, Popup, CircleMarker } from 'react-leaflet';
import { Button, Card, Typography, message } from 'antd';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';

const { Title, Text } = Typography;

// Fix for default marker icons in React-Leaflet (not needed for CircleMarker, but kept for compatibility)
import icon from 'leaflet/dist/images/marker-icon.png';
import iconShadow from 'leaflet/dist/images/marker-shadow.png';
import iconRetina from 'leaflet/dist/images/marker-icon-2x.png';

delete (L.Icon.Default.prototype as any)._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: iconRetina,
  iconUrl: icon,
  shadowUrl: iconShadow,
});

// Mock Data
const MOCK_FIGHTERS = [
  { id: 'f1', callsign: 'J-20-01', lat: 34.2, lng: 108.9, status: 'Ready' },
  { id: 'f2', callsign: 'J-16-05', lat: 34.3, lng: 109.1, status: 'In-Air' },
];

const MOCK_TARGETS = [
  { id: 't1', name: 'Enemy Radar', lat: 34.25, lng: 109.0, threat: 'High' },
];

// Map center (demo location)
const MAP_CENTER: [number, number] = [34.25, 109.0];
const MAP_ZOOM = 10;

const Dashboard: React.FC = () => {
  // Handle strike action
  const handleStrike = (targetId: string, targetName: string) => {
    console.log('Strike triggered on target:', targetId);
    message.success(`执行打击: ${targetName}`);
  };

  return (
    <div style={{ width: '100%', height: 'calc(100vh - 48px)', position: 'relative' }}>
      <MapContainer
        center={MAP_CENTER}
        zoom={MAP_ZOOM}
        style={{ width: '100%', height: '100%', zIndex: 1 }}
        scrollWheelZoom={true}
      >
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />

        {/* Render Fighters as Blue CircleMarkers */}
        {MOCK_FIGHTERS.map((fighter) => (
          <CircleMarker
            key={fighter.id}
            center={[fighter.lat, fighter.lng]}
            radius={8}
            pathOptions={{
              color: '#1890ff',
              fillColor: '#1890ff',
              fillOpacity: 0.8,
              weight: 2,
            }}
          >
            <Popup>
              <Card size="small" style={{ minWidth: 150 }}>
                <Title level={5} style={{ margin: 0, marginBottom: 8 }}>
                  {fighter.callsign}
                </Title>
                <Text type="secondary">Status: {fighter.status}</Text>
              </Card>
            </Popup>
          </CircleMarker>
        ))}

        {/* Render Targets as Red CircleMarkers */}
        {MOCK_TARGETS.map((target) => (
          <CircleMarker
            key={target.id}
            center={[target.lat, target.lng]}
            radius={10}
            pathOptions={{
              color: '#ff4d4f',
              fillColor: '#ff4d4f',
              fillOpacity: 0.8,
              weight: 2,
            }}
          >
            <Popup>
              <Card size="small" style={{ minWidth: 200 }}>
                <Title level={5} style={{ margin: 0, marginBottom: 8 }}>
                  {target.name}
                </Title>
                <Text type="secondary" style={{ display: 'block', marginBottom: 12 }}>
                  Threat Level: {target.threat}
                </Text>
                <Button
                  type="primary"
                  danger
                  block
                  onClick={() => handleStrike(target.id, target.name)}
                >
                  执行打击
                </Button>
              </Card>
            </Popup>
          </CircleMarker>
        ))}
      </MapContainer>
    </div>
  );
};

export default Dashboard;
