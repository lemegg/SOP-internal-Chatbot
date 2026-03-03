import React from 'react';
import SourcesAccordion from './SourcesAccordion';

const MessageBubble = ({ message }) => {
  const isUser = message.sender === 'user';
  
  if (isUser) {
    return (
      <div className="message user">
        <div className="text">{message.text}</div>
      </div>
    );
  }

  // Bot message rendering for structured answer
  const { summary, steps, rules, notes } = message.answer || {};

  return (
    <div className="message bot">
      <div className="bot-content">
        {message.text && <p className="summary">{message.text}</p>}
        {summary && <p className="summary">{summary}</p>}
        
        {steps && steps.length > 0 && (
          <div className="section">
            <h4 className="section-title">Steps:</h4>
            <ol className="steps-list">
              {steps.map((step, i) => <li key={i}>{step}</li>)}
            </ol>
          </div>
        )}

        {rules && rules.length > 0 && (
          <div className="section">
            <h4 className="section-title">Policies & Rules:</h4>
            <ul className="rules-list">
              {rules.map((rule, i) => <li key={i}>{rule}</li>)}
            </ul>
          </div>
        )}

        {notes && notes.length > 0 && (
          <div className="section notes-section">
            {notes.map((note, i) => <p key={i} className="note-item small">{note}</p>)}
          </div>
        )}
      </div>

      <SourcesAccordion sources={message.sources} />
    </div>
  );
};

export default MessageBubble;
