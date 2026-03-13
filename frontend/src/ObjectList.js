import React from 'react';

function ObjectList({ objects }) {
  return (
    <div className="card shadow-sm h-100">
      <div className="card-header">Detected Objects</div>
      <ul className="list-group list-group-flush">
        {objects.length === 0 ? (
          <li className="list-group-item text-muted">No detections yet.</li>
        ) : (
          objects.map((obj, index) => (
            <li className="list-group-item" key={`${obj.label}-${index}`}>
              <strong>{obj.label}</strong> ({(obj.confidence * 100).toFixed(1)}%)
            </li>
          ))
        )}
      </ul>
    </div>
  );
}

export default ObjectList;
