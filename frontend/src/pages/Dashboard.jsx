import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';

const Dashboard = () => {
  const [activeTab, setActiveTab] = useState('top-queries');
  const [range, setRange] = useState('weekly');
  const [data, setData] = useState(null);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);
  const { token } = useAuth();

  useEffect(() => {
    const fetchAnalytics = async () => {
      setLoading(true);
      setError(null);
      const api_base = window.location.origin.includes('localhost') || window.location.origin.includes('127.0.0.1') ? 'http://127.0.0.1:8000' : '';
      
      let url = `${api_base}/api/analytics/top-queries?range=${range}`;
      if (activeTab === 'query-log') {
        url = `${api_base}/api/analytics/query-log/monthly`;
      }

      try {
        const response = await fetch(url, {
          headers: { 'Authorization': `Bearer ${token}` }
        });
        if (!response.ok) {
          if (response.status === 403) throw new Error('Not authorized to access analytics');
          throw new Error('Failed to fetch data');
        }
        const result = await response.json();
        setData(result);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };
    fetchAnalytics();
  }, [range, activeTab, token]);

  if (error) return <div className="dashboard-error">Access Denied: {error}</div>;

  return (
    <div className="dashboard-container">
      <header className="dashboard-header">
        <h1>Analytics Dashboard</h1>
        <div className="tabs">
          <button 
            className={`tab-btn ${activeTab === 'top-queries' ? 'active' : ''}`}
            onClick={() => setActiveTab('top-queries')}
          >
            Top Queries
          </button>
          <button 
            className={`tab-btn ${activeTab === 'query-log' ? 'active' : ''}`}
            onClick={() => setActiveTab('query-log')}
          >
            Monthly Query Log
          </button>
        </div>
      </header>

      {loading ? (
        <div className="loading-state">Loading dashboard data...</div>
      ) : (
        <>
          {activeTab === 'top-queries' && data?.top_queries && (
            <div className="queries-list">
              <div className="list-header">
                <h3>Top 15 Queries ({range})</h3>
                <div className="range-toggle">
                  <button className={range === 'weekly' ? 'active' : ''} onClick={() => setRange('weekly')}>Weekly</button>
                  <button className={range === 'monthly' ? 'active' : ''} onClick={() => setRange('monthly')}>Monthly</button>
                </div>
              </div>
              <table>
                <thead>
                  <tr>
                    <th>Rank</th>
                    <th>Query</th>
                    <th>Count</th>
                  </tr>
                </thead>
                <tbody>
                  {data.top_queries.map((item, index) => (
                    <tr key={index}>
                      <td>{index + 1}</td>
                      <td>{item.query}</td>
                      <td>{item.count}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}

          {activeTab === 'query-log' && data?.logs && (
            <div className="queries-list">
              <h3>Monthly Query Log (Last 30 Days)</h3>
              <div className="scrollable-table">
                <table>
                  <thead>
                    <tr>
                      <th>Query</th>
                      <th>Timestamp</th>
                      <th>Person</th>
                      <th>Feedback</th>
                    </tr>
                  </thead>
                  <tbody>
                    {data.logs.map((log, index) => (
                      <tr key={index}>
                        <td>{log.query}</td>
                        <td style={{ whiteSpace: 'nowrap' }}>{new Date(log.timestamp).toLocaleString()}</td>
                        <td>{log.person}</td>
                        <td style={{ textAlign: 'center' }}>
                          {log.feedback === 'like' ? '👍' : log.feedback === 'dislike' ? '👎' : '—'}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}
        </>
      )}
    </div>
  );
};

export default Dashboard;
