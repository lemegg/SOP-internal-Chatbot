import React, { useEffect, useRef } from 'react';
import MessageBubble from './MessageBubble';

const ChatWindow = ({ messages, isThinking }) => {
  const scrollRef = useRef(null);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages, isThinking]);

  return (
    <div className="chat-window" ref={scrollRef}>
      {messages.map((msg, index) => (
        <MessageBubble key={index} message={msg} />
      ))}
      {isThinking && <div className="thinking">Thinking...</div>}
    </div>
  );
};

export default ChatWindow;
