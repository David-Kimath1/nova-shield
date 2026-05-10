// src/App.js
import React, { useState, useEffect, useRef } from 'react';
import io from 'socket.io-client';
import { Activity, Shield, AlertTriangle, Lock, Camera, Cpu, HardDrive } from 'lucide-react';
import { LineChart, Line, Area, AreaChart, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts';

const socket = io('http://localhost:5000');

function App() {
  const [dashboardData, setDashboardData] = useState({
    security_score: 95,
    threat_level: 'GREEN',
    current_face: null,
    gpu_available: false,
    fps: 0,
    intruder_count: 0,
    recent_events: []
  });
  const [systemStats, setSystemStats] = useState({ cpu: 0, memory: 0, gpu: null });
  const [intruders, setIntruders] = useState([]);
  const [performanceHistory, setPerformanceHistory] = useState([]);

  useEffect(() => {
    socket.on('connect', () => console.log('Connected to NOVA-SHIELD'));
    socket.on('dashboard_data', (data) => setDashboardData(data));
    socket.on('system_stats', (stats) => {
      setSystemStats(stats);
      setPerformanceHistory(prev => [...prev.slice(-20), { time: new Date().toLocaleTimeString(), ...stats }]);
    });
    socket.on('intruder_list', (data) => setIntruders(data));
    
    socket.emit('request_intruders');
    
    return () => socket.disconnect();
  }, []);

  const getThreatColor = (level) => {
    const colors = { GREEN: '#10b981', YELLOW: '#f59e0b', ORANGE: '#f97316', RED: '#ef4444' };
    return colors[level] || '#6b7280';
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 to-gray-800 text-white">
      {/* Header */}
      <header className="bg-gray-900/50 backdrop-blur-lg border-b border-gray-700 px-6 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <Shield className="w-8 h-8 text-purple-500" />
            <h1 className="text-2xl font-bold bg-gradient-to-r from-purple-400 to-pink-400 bg-clip-text text-transparent">
              NOVA-SHIELD
            </h1>
          </div>
          <div className="flex items-center space-x-4">
            <div className="flex items-center space-x-2">
              <Activity className="w-4 h-4 text-green-400" />
              <span className="text-sm">Active</span>
            </div>
            <div className="px-3 py-1 rounded-full text-sm font-semibold"
                 style={{ backgroundColor: getThreatColor(dashboardData.threat_level) + '20', color: getThreatColor(dashboardData.threat_level) }}>
              {dashboardData.threat_level} THREAT LEVEL
            </div>
          </div>
        </div>
      </header>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 p-6">
        {/* Security Score Card */}
        <div className="bg-gray-800/50 backdrop-blur rounded-xl border border-gray-700 p-6">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-semibold">Security Score</h2>
            <Shield className="w-5 h-5 text-purple-400" />
          </div>
          <div className="text-center">
            <div className="text-6xl font-bold text-purple-400">{dashboardData.security_score}%</div>
            <div className="text-sm text-gray-400 mt-2">Trust Level</div>
          </div>
          <div className="mt-4 h-2 bg-gray-700 rounded-full overflow-hidden">
            <div className="h-full bg-purple-500 rounded-full transition-all" 
                 style={{ width: `${dashboardData.security_score}%` }} />
          </div>
        </div>

        {/* System Stats */}
        <div className="bg-gray-800/50 backdrop-blur rounded-xl border border-gray-700 p-6">
          <h2 className="text-lg font-semibold mb-4">System Status</h2>
          <div className="space-y-3">
            <div className="flex justify-between items-center">
              <div className="flex items-center space-x-2">
                <Cpu className="w-4 h-4 text-blue-400" />
                <span className="text-sm">CPU</span>
              </div>
              <span className="text-sm font-mono">{systemStats.cpu}%</span>
            </div>
            <div className="flex justify-between items-center">
              <div className="flex items-center space-x-2">
                <HardDrive className="w-4 h-4 text-green-400" />
                <span className="text-sm">RAM</span>
              </div>
              <span className="text-sm font-mono">{systemStats.memory}%</span>
            </div>
            <div className="flex justify-between items-center">
              <div className="flex items-center space-x-2">
                <Camera className="w-4 h-4 text-yellow-400" />
                <span className="text-sm">FPS</span>
              </div>
              <span className="text-sm font-mono">{dashboardData.fps} FPS</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-sm">GPU</span>
              <span className={`text-sm font-mono ${dashboardData.gpu_available ? 'text-green-400' : 'text-gray-500'}`}>
                {dashboardData.gpu_available ? 'CUDA Active' : 'CPU Mode'}
              </span>
            </div>
          </div>
        </div>

        {/* Threat Timeline */}
        <div className="bg-gray-800/50 backdrop-blur rounded-xl border border-gray-700 p-6">
          <h2 className="text-lg font-semibold mb-4">Recent Events</h2>
          <div className="space-y-2 max-h-48 overflow-y-auto">
            {dashboardData.recent_events.map((event, i) => (
              <div key={i} className="flex items-center space-x-2 text-sm p-2 bg-gray-900/50 rounded">
                <AlertTriangle className="w-3 h-3 text-yellow-500" />
                <span className="text-gray-300">{event}</span>
              </div>
            ))}
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 p-6">
        {/* Performance Chart */}
        <div className="bg-gray-800/50 backdrop-blur rounded-xl border border-gray-700 p-6">
          <h2 className="text-lg font-semibold mb-4">Performance Monitor</h2>
          <ResponsiveContainer width="100%" height={200}>
            <AreaChart data={performanceHistory}>
              <XAxis dataKey="time" stroke="#6b7280" />
              <YAxis stroke="#6b7280" />
              <Tooltip contentStyle={{ backgroundColor: '#1f2937', border: 'none' }} />
              <Area type="monotone" dataKey="cpu" stroke="#3b82f6" fill="#3b82f620" />
              <Area type="monotone" dataKey="memory" stroke="#10b981" fill="#10b98120" />
            </AreaChart>
          </ResponsiveContainer>
        </div>

        {/* Intruder Gallery */}
        <div className="bg-gray-800/50 backdrop-blur rounded-xl border border-gray-700 p-6">
          <h2 className="text-lg font-semibold mb-4">Intruder Detection ({dashboardData.intruder_count})</h2>
          <div className="grid grid-cols-3 gap-2 max-h-48 overflow-y-auto">
            {intruders.map((intruder, i) => (
              <div key={i} className="relative group">
                <img src={intruder.path} alt="Intruder" className="w-full h-24 object-cover rounded-lg" />
                <div className="absolute inset-0 bg-red-500/0 group-hover:bg-red-500/20 transition-all rounded-lg" />
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;