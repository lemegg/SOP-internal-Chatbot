import React, { createContext, useState, useContext, useEffect } from 'react';

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [token, setToken] = useState(null);
  const [loading, setLoading] = useState(true);

  const login = async (email, password) => {
    const formData = new FormData();
    formData.append('username', email);
    formData.append('password', password);

    const response = await fetch('http://127.0.0.1:8000/auth/login', {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) throw new Error('Login failed');

    const data = await response.json();
    setToken(data.access_token);
    
    // Fetch user profile
    const userRes = await fetch('http://127.0.0.1:8000/auth/me', {
      headers: { 'Authorization': `Bearer ${data.access_token}` }
    });
    const userData = await userRes.json();
    setUser(userData);
    return userData;
  };

  const logout = () => {
    setUser(null);
    setToken(null);
  };

  useEffect(() => {
    // For MVP, we'll stay logged out on refresh unless we implement persistence.
    // User requested token in memory (not localStorage).
    setLoading(false);
  }, []);

  return (
    <AuthContext.Provider value={{ user, token, login, logout, loading }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => useContext(AuthContext);
