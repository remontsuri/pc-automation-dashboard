import { useState, useEffect } from 'react';
import axios from 'axios';
import './App.css';

const API_URL = 'http://localhost:8000/api';

function App() {
  const [systemInfo, setSystemInfo] = useState(null);
  const [processes, setProcesses] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [filter, setFilter] = useState('');

  useEffect(() => {
    fetchSystemInfo();
    const interval = setInterval(fetchSystemInfo, 5000);
    return () => clearInterval(interval);
  }, []);

  const fetchSystemInfo = async () => {
    try {
      setLoading(true);
      const response = await axios.get(`${API_URL}/system-info`);
      setSystemInfo(response.data);
      setError(null);
    } catch (err) {
      setError('Failed to fetch system info');
    } finally {
      setLoading(false);
    }
  };

  const fetchProcesses = async () => {
    try {
      setLoading(true);
      const response = await axios.get(`${API_URL}/processes`);
      setProcesses(response.data);
    } catch (err) {
      setError('Failed to fetch processes');
    } finally {
      setLoading(false);
    }
  };

  const killProcess = async (pid) => {
    try {
      await axios.post(`${API_URL}/kill-process`, { pid });
      fetchProcesses();
    } catch (err) {
      setError('Failed to kill process');
    }
  };

  const filteredProcesses = processes.filter(p =>
    p.name.toLowerCase().includes(filter.toLowerCase())
  );

  return (
    <div className="App">
      <header className="header">
        <h1>PC Activity Automation Dashboard</h1>
        <p>Real-time Windows Process Monitoring</p>
      </header>

      {error && <div className="error">{error}</div>}

      <div className="dashboard">
        {systemInfo && (
          <div className="info-card">
            <h2>System Information</h2>
            <div className="info-grid">
              <div>CPU Usage: {systemInfo.cpu_percent}%</div>
              <div>Memory: {systemInfo.memory_percent}%</div>
              <div>Disk: {systemInfo.disk_percent}%</div>
              <div>Processes: {systemInfo.process_count}</div>
            </div>
          </div>
        )}

        <div className="processes-card">
          <div className="card-header">
            <h2>Running Processes</h2>
            <button onClick={fetchProcesses} className="btn-refresh">Refresh</button>
          </div>
          <input
            type="text"
            placeholder="Search processes..."
            value={filter}
            onChange={(e) => setFilter(e.target.value)}
            className="search-input"
          />
          <div className="processes-list">
            {filteredProcesses.map(proc => (
              <div key={proc.pid} className="process-item">
                <span className="process-name">{proc.name}</span>
                <span className="process-memory">{proc.memory}MB</span>
                <button
                  onClick={() => killProcess(proc.pid)}
                  className="btn-kill"
                  title="Kill process"
                >×</button>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;
