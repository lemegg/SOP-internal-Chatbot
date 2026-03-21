import React from 'react';
import { SignIn } from '@clerk/clerk-react';

const Login = () => {
  return (
    <div className="login-container">
      <div className="login-card">
        <h1>SOP Assistant</h1>
        <p>Please sign in to access the chatbot</p>
        <div style={{ display: 'flex', justifyContent: 'center', marginTop: '20px' }}>
          <SignIn />
        </div>
      </div>
    </div>
  );
};

export default Login;
