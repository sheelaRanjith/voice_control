import React from 'react';

function VideoFeed({ isRunning, backendUrl }) {
  const src = isRunning ? `${backendUrl}/video_feed` : '';

  return (
    <div className="card shadow-sm h-100">
      <div className="card-header">Live Video</div>
      <div className="card-body d-flex align-items-center justify-content-center video-panel">
        {isRunning ? (
          <img src={src} alt="Live stream" className="img-fluid rounded border" />
        ) : (
          <p className="text-muted mb-0">Press Start to begin video streaming.</p>
        )}
      </div>
    </div>
  );
}

export default VideoFeed;
