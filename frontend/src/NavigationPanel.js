import React from 'react';

function NavigationPanel({ feedback, feedbackAt, onReplay }) {
  return (
    <div className="card shadow-sm h-100">
      <div className="card-header d-flex justify-content-between align-items-center">
        <span>Navigation Feedback</span>
        <small className="text-muted">{feedbackAt ? new Date(feedbackAt).toLocaleTimeString() : 'No updates'}</small>
      </div>
      <div className="card-body d-grid gap-2">
        <p className="mb-0">{feedback || 'Awaiting navigation updates...'}</p>
        <button className="btn btn-sm btn-outline-secondary" onClick={onReplay} disabled={!feedback}>
          Replay Audio
        </button>
      </div>
    </div>
  );
}

export default NavigationPanel;
