import React, { useState } from 'react';

const SourcesAccordion = ({ sources }) => {
  const [isOpen, setIsOpen] = useState(false);

  if (!sources || sources.length === 0) return null;

  return (
    <div className="sources-accordion">
      <button 
        className="accordion-trigger" 
        onClick={() => setIsOpen(!isOpen)}
      >
        {isOpen ? 'Collapse Sources' : 'View Sources'}
      </button>
      
      <div className={`accordion-content ${isOpen ? 'open' : ''}`}>
        {sources.map((source, index) => (
          <div key={index} className="source-item">
            {source.sop} — {source.section}
          </div>
        ))}
      </div>
    </div>
  );
};

export default SourcesAccordion;
