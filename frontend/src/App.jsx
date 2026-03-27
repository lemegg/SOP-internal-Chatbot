import React, { useState } from 'react';
import ChatWindow from './components/ChatWindow';
import ChatInput from './components/ChatInput';
import Login from './pages/Login';
import Dashboard from './pages/Dashboard';
import { SignedIn, SignedOut, SignOutButton, useUser, useAuth } from '@clerk/clerk-react';

const ChatInterface = () => {
  const [messages, setMessages] = useState([
    {
      sender: 'bot',
      text: 'Hello! I am your SOP Assistant. How can I help you today?',
    }
  ]);
  const [loading, setLoading] = useState(false);
  const { getToken } = useAuth();
  const { user } = useUser();
  const [showDashboard, setShowDashboard] = useState(false);

  const isAdmin = user?.publicMetadata?.role === 'admin' || user?.emailAddresses.some(e => 
    ["worshipgate1@gmail.com", "sruthi@theaffordableorganicstore.com", "anurag@theaffordableorganicstore.com", "shivam@theaffordableorganicstore.com"].includes(e.emailAddress.toLowerCase())
  );

  const handleSendMessage = async (text) => {
    const userMsg = { sender: 'user', text };
    setMessages((prev) => [...prev, userMsg]);
    setLoading(true);

    try {
      const token = await getToken();
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
        query_log_id: data.query_log_id,
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

  if (showDashboard) return (
    <>
      <button className="nav-btn" onClick={() => setShowDashboard(false)}>Back to Chat</button>
      <Dashboard />
    </>
  );

  return (
    <div id="root">
      <header className="app-header">
        <span className="user-email">{user?.primaryEmailAddress?.emailAddress}</span>
        <div className="header-actions">
          {isAdmin && (
            <button onClick={() => setShowDashboard(true)}>Dashboard</button>
          )}
          <SignOutButton className="logout-btn" />
        </div>
      </header>
      <ChatWindow messages={messages} isThinking={loading} />
      <ChatInput onSendMessage={handleSendMessage} disabled={loading} />
    </div>
  );
};

const App = () => (
  <>
    <SignedIn>
      <ChatInterface />
    </SignedIn>
    <SignedOut>
      <Login />
    </SignedOut>
  </>
);

export default App;
