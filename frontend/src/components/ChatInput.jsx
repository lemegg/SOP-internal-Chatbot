import React, { useState } from 'react';

const ChatInput = ({ onSendMessage, disabled }) => {
  const [input, setInput] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    if (input.trim() && !disabled) {
      onSendMessage(input.trim());
      setInput('');
    }
  };

  return (
    <div className="chat-input-container">
      <form className="chat-input-wrapper" onSubmit={handleSubmit}>
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Type your question here..."
          disabled={disabled}
        />
        <button type="submit" disabled={disabled || !input.trim()}>
          Send
        </button>
      </form>
    </div>
  );
};

export default ChatInput;
