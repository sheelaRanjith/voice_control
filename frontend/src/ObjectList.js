import React from 'react';

function ObjectList({ objects, updatedAt }) {
  return (
    <div className="card shadow-sm h-100">
      <div className="card-header d-flex justify-content-between align-items-center">
        <span>Detected Objects</span>
        <small className="text-muted">{updatedAt ? new Date(updatedAt * 1000).toLocaleTimeString() : 'No updates'}</small>
      </div>
      <ul className="list-group list-group-flush">
        {objects.length === 0 ? (
          <li className="list-group-item text-muted">No detections yet.</li>
        ) : (
          objects.map((obj, index) => (
            <li className="list-group-item" key={`${obj.label}-${index}`}>
              <div className="d-flex justify-content-between">
                <strong>{obj.label}</strong>
                <span>{(obj.confidence * 100).toFixed(1)}%</span>
              </div>
              <div className="progress my-1" role="progressbar" aria-label="confidence">
                <div className="progress-bar" style={{ width: `${Math.round(obj.confidence * 100)}%` }} />
              </div>
              <small className="text-muted">{obj.position} / {obj.distance_hint} • x:{obj.x}, y:{obj.y}</small>
            </li>
          ))
        )}
      </ul>
    </div>
  );
}

export default ObjectList;
