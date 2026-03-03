import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';

const Dashboard = () => {
  const [range, setRange] = useState('weekly');
  const [data, setData] = useState(null);
  const [error, setError] = useState(null);
  const { token } = useAuth();

  useEffect(() => {
    const fetchAnalytics = async () => {
      const api_base = window.location.origin.includes('localhost') || window.location.origin.includes('127.0.0.1') ? 'http://127.0.0.1:8000' : '';
      try {
        const response = await fetch(`${api_base}/api/analytics/top-queries?range=${range}`, {
          headers: { 'Authorization': `Bearer ${token}` }
        });
        if (!response.ok) throw new Error('Unauthorized');
        const result = await response.json();
        setData(result);
      } catch (err) {
        setError(err.message);
      }
    };
    fetchAnalytics();
  }, [range, token]);

  if (error) return <div className="dashboard-error">Access Denied: {error}</div>;
  if (!data) return <div>Loading...</div>;

  return (
    <div className="dashboard-container">
      <header className="dashboard-header">
        <h1>Analytics Dashboard</h1>
        <div className="range-toggle">
          <button className={range === 'weekly' ? 'active' : ''} onClick={() => setRange('weekly')}>Weekly</button>
          <button className={range === 'monthly' ? 'active' : ''} onClick={() => setRange('monthly')}>Monthly</button>
        </div>
      </header>

      <div className="queries-list">
        <h3>Top 15 Queries ({range})</h3>
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
    </div>
  );
};

export default Dashboard;
