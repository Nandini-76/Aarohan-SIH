import React, { useState, useEffect } from 'react';
import { renderPingService } from '../services/renderPing';

/**
 * Development component to show Render ping status
 * Only visible in development mode
 */
const RenderPingStatus: React.FC = () => {
  const [status, setStatus] = useState(renderPingService.getStatus());
  const [lastPing, setLastPing] = useState<string>('Never');

  useEffect(() => {
    // Update status every 10 seconds
    const statusInterval = setInterval(() => {
      setStatus(renderPingService.getStatus());
    }, 10000);

    // Listen for ping events by capturing console.log (hacky but works for dev)
    const originalLog = console.log;
    console.log = (...args) => {
      originalLog(...args);
      if (args[0]?.includes?.('🏓 Render ping successful')) {
        setLastPing(new Date().toLocaleTimeString());
      }
    };

    return () => {
      clearInterval(statusInterval);
      console.log = originalLog;
    };
  }, []);

  // Only show in development
  if (import.meta.env.PROD) {
    return null;
  }

  return (
    <div
      style={{
        position: 'fixed',
        bottom: '10px',
        right: '10px',
        backgroundColor: status.isActive ? '#dcfce7' : '#fee2e2',
        border: `1px solid ${status.isActive ? '#16a34a' : '#dc2626'}`,
        borderRadius: '8px',
        padding: '8px 12px',
        fontSize: '12px',
        fontFamily: 'monospace',
        zIndex: 9999,
        maxWidth: '250px',
      }}
    >
      <div style={{ fontWeight: 'bold' }}>
        🏓 Render Ping: {status.isActive ? '✅ Active' : '❌ Inactive'}
      </div>
      <div>Interval: {Math.round(status.interval / 1000)}s</div>
      <div>Last ping: {lastPing}</div>
      <div style={{ fontSize: '10px', marginTop: '4px', opacity: 0.7 }}>
        (Dev only - hidden in production)
      </div>
    </div>
  );
};

export default RenderPingStatus;