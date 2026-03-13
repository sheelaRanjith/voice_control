import React from 'react';

function NavigationPanel({ feedback }) {
  return (
    <div className="card shadow-sm h-100">
      <div className="card-header">Navigation Feedback</div>
      <div className="card-body">
        <p className="mb-0">{feedback || 'Awaiting navigation updates...'}</p>
      </div>
    </div>
  );
}

export default NavigationPanel;
