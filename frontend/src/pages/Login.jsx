import React from 'react';
import { SignIn, SignUp } from '@clerk/clerk-react';

const Login = () => {
  // Check if we are in an invitation flow
  const isInvitation = window.location.search.includes('__clerk_ticket');

  return (
    <div className="login-container">
      <div className="login-card">
        <h1>SOP Assistant</h1>
        {isInvitation ? (
          <>
            <p>Welcome! Please create your account to accept the invitation.</p>
            <div style={{ display: 'flex', justifyContent: 'center', marginTop: '20px' }}>
              <SignUp signInUrl="/" />
            </div>
          </>
        ) : (
          <>
            <p>Please sign in to access the chatbot</p>
            <div style={{ display: 'flex', justifyContent: 'center', marginTop: '20px' }}>
              <SignIn signUpUrl="/?__clerk_status=sign_up" />
            </div>
          </>
        )}
      </div>
    </div>
  );
};

export default Login;
