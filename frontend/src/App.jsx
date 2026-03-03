import React, { useState } from 'react';
import ChatWindow from './components/ChatWindow';
import ChatInput from './components/ChatInput';
import Login from './pages/Login';
import Dashboard from './pages/Dashboard';
import { AuthProvider, useAuth } from './context/AuthContext';

const ChatInterface = () => {
  const [messages, setMessages] = useState([
    {
      sender: 'bot',
      text: 'Hello! I am your SOP Assistant. How can I help you today?',
    }
  ]);
  const [loading, setLoading] = useState(false);
  const { token, logout, user } = useAuth();
  const [showDashboard, setShowDashboard] = useState(false);

  const handleSendMessage = async (text) => {
    const userMsg = { sender: 'user', text };
    setMessages((prev) => [...prev, userMsg]);
    setLoading(true);

    try {
      const api_url = window.location.origin.includes('localhost') || window.location.origin.includes('127.0.0.1')
        ? 'http://127.0.0.1:8000/api/chat' 
        : '/api/chat';

      const response = await fetch(api_url, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({ query: text }),
      });

      if (!response.ok) throw new Error('Failed to fetch');

      const data = await response.json();
      setMessages((prev) => [...prev, {
        sender: 'bot',
        answer: data.answer,
        sources: data.sources,
      }]);
    } catch (error) {
      setMessages((prev) => [...prev, {
        sender: 'bot',
        text: 'Server error. Please try again.',
      }]);
    } finally {
      setLoading(false);
    }
  };

  if (!token) return <Login />;
  if (showDashboard) return (
    <>
      <button className="nav-btn" onClick={() => setShowDashboard(false)}>Back to Chat</button>
      <Dashboard />
    </>
  );

  return (
    <div id="root">
      <header className="app-header">
        <span className="user-email">{user?.email}</span>
        <div className="header-actions">
          {["manager@company.com", "anurag@theaffordableorganicstore.com"].includes(user?.email) && (
            <button onClick={() => setShowDashboard(true)}>Dashboard</button>
          )}
          <button onClick={logout}>Logout</button>
        </div>
      </header>
      <ChatWindow messages={messages} isThinking={loading} />
      <ChatInput onSendMessage={handleSendMessage} disabled={loading} />
    </div>
  );
};

const App = () => (
  <AuthProvider>
    <ChatInterface />
  </AuthProvider>
);

export default App;
