import React, { useState, useEffect } from 'react';
import { useAuth } from '@clerk/clerk-react';

const Dashboard = () => {
  const [activeTab, setActiveTab] = useState('top-queries');
  const [range, setRange] = useState('weekly');
  const [data, setData] = useState(null);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);
  const { getToken } = useAuth();

  useEffect(() => {
    const fetchAnalytics = async () => {
      setLoading(true);
      setError(null);
      const api_base = window.location.origin.includes('localhost') || window.location.origin.includes('127.0.0.1') ? 'http://127.0.0.1:8000' : '';
      
      let url = `${api_base}/api/analytics/top-queries?range=${range}`;
      if (activeTab === 'query-log') {
        url = `${api_base}/api/analytics/query-log/monthly`;
      } else if (activeTab === 'sop-missed') {
        url = `${api_base}/api/analytics/sop-missed`;
      }

      try {
        const token = await getToken();
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
  }, [range, activeTab, getToken]);

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
          <button 
            className={`tab-btn ${activeTab === 'sop-missed' ? 'active' : ''}`}
            onClick={() => setActiveTab('sop-missed')}
          >
            SOP Missed Queries
          </button>
          <button 
            className={`tab-btn ${activeTab === 'users' ? 'active' : ''}`}
            onClick={() => setActiveTab('users')}
          >
            User Management
          </button>
        </div>
      </header>

      {loading ? (
        <div className="loading-state">Loading dashboard data...</div>
      ) : (
        <>
          {activeTab === 'users' && <UserManagement getToken={getToken} />}
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
                    <th>👍 Positive %</th>
                    <th>👎 Negative %</th>
                  </tr>
                </thead>
                <tbody>
                  {data.top_queries.map((item, index) => (
                    <tr key={index}>
                      <td>{item.rank}</td>
                      <td>{item.query}</td>
                      <td>{item.count}</td>
                      <td>{item.positive_percent !== null ? `${item.positive_percent}%` : '—'}</td>
                      <td>{item.negative_percent !== null ? `${item.negative_percent}%` : '—'}</td>
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

          {activeTab === 'sop-missed' && data?.logs && (
            <div className="queries-list">
              <h3>SOP Missed Queries (Information Not Found)</h3>
              <div className="scrollable-table">
                <table>
                  <thead>
                    <tr>
                      <th>Query</th>
                      <th>Timestamp</th>
                      <th>Person</th>
                    </tr>
                  </thead>
                  <tbody>
                    {data.logs.map((log, index) => (
                      <tr key={index}>
                        <td>{log.query}</td>
                        <td style={{ whiteSpace: 'nowrap' }}>{new Date(log.timestamp).toLocaleString()}</td>
                        <td>{log.person}</td>
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

const UserManagement = ({ getToken }) => {
  const [data, setData] = useState({ active_users: [], pending_invites: [] });
  const [loading, setLoading] = useState(true);
  const [email, setEmail] = useState('');
  const [msg, setMsg] = useState({ type: '', text: '' });

  const api_base = window.location.origin.includes('localhost') || window.location.origin.includes('127.0.0.1') ? 'http://127.0.0.1:8000' : '';

  const fetchData = async () => {
    setLoading(true);
    try {
      const token = await getToken();
      const resp = await fetch(`${api_base}/api/admin/users`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (!resp.ok) throw new Error('Failed to fetch users');
      setData(await resp.json());
    } catch (err) {
      setMsg({ type: 'error', text: err.message });
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { fetchData(); }, []);

  const handleInvite = async (e) => {
    e.preventDefault();
    setMsg({ type: '', text: '' });
    try {
      const token = await getToken();
      const resp = await fetch(`${api_base}/api/admin/invite`, {
        method: 'POST',
        headers: { 
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ email })
      });
      if (!resp.ok) {
        const d = await resp.json();
        throw new Error(d.detail || 'Invite failed');
      }
      setMsg({ type: 'success', text: `Invitation sent to ${email}` });
      setEmail('');
      fetchData();
    } catch (err) {
      setMsg({ type: 'error', text: err.message });
    }
  };

  const handleAction = async (url, method = 'POST') => {
    if (!window.confirm('Are you sure?')) return;
    try {
      const token = await getToken();
      const resp = await fetch(`${api_base}${url}`, {
        method,
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (!resp.ok) throw new Error('Action failed');
      fetchData();
    } catch (err) {
      setMsg({ type: 'error', text: err.message });
    }
  };

  return (
    <div className="user-management">
      <div className="invite-box">
        <h3>Grant Access (Invite by Email)</h3>
        <form onSubmit={handleInvite}>
          <input 
            type="email" 
            placeholder="colleague@example.com" 
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
          />
          <button type="submit">Invite User</button>
        </form>
        {msg.text && <p className={`status-msg ${msg.type}`}>{msg.text}</p>}
      </div>

      <div className="users-lists">
        <div className="list-section">
          <h3>Active Users ({data.active_users.length})</h3>
          <table>
            <thead>
              <tr><th>Email</th><th>Joined</th><th>Action</th></tr>
            </thead>
            <tbody>
              {data.active_users.map(u => (
                <tr key={u.id}>
                  <td>{u.email}</td>
                  <td>{new Date(u.joined_at).toLocaleDateString()}</td>
                  <td>
                    <button onClick={() => handleAction(`/api/admin/users/${u.id}`, 'DELETE')} className="revoke-btn">Revoke Access</button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        <div className="list-section">
          <h3>Pending Invitations ({data.pending_invites.length})</h3>
          <table>
            <thead>
              <tr><th>Email</th><th>Sent</th><th>Action</th></tr>
            </thead>
            <tbody>
              {data.pending_invites.map(i => (
                <tr key={i.id}>
                  <td>{i.email}</td>
                  <td>{new Date(i.sent_at).toLocaleDateString()}</td>
                  <td>
                    <button onClick={() => handleAction(`/api/admin/invitations/${i.id}/revoke`)} className="revoke-btn">Cancel Invite</button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
