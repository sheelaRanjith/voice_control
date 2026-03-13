import React, { useEffect, useMemo, useState } from 'react';
import axios from 'axios';
import VideoFeed from './VideoFeed';
import ObjectList from './ObjectList';
import VoiceControl from './VoiceControl';
import NavigationPanel from './NavigationPanel';

function App() {
  const backendUrl = useMemo(() => process.env.REACT_APP_BACKEND_URL || 'http://localhost:8000', []);
  const [isRunning, setIsRunning] = useState(false);
  const [objects, setObjects] = useState([]);
  const [lastCommand, setLastCommand] = useState('None');
  const [feedback, setFeedback] = useState('');
  const [theme, setTheme] = useState('light');
  const [snapshotUrl, setSnapshotUrl] = useState('');

  useEffect(() => {
    if (!isRunning) {
      return undefined;
    }

    const interval = setInterval(async () => {
      try {
        const [objectsRes, navRes] = await Promise.all([
          axios.get(`${backendUrl}/detect_objects`),
          axios.get(`${backendUrl}/navigation_feedback`)
        ]);
        setObjects(objectsRes.data.objects || []);
        setFeedback(navRes.data.feedback || '');
      } catch {
        // Keep UI responsive if backend is temporarily unavailable.
      }
    }, 1000);

    return () => clearInterval(interval);
  }, [isRunning, backendUrl]);

  const resetState = () => {
    setObjects([]);
    setLastCommand('None');
    setFeedback('');
    setSnapshotUrl('');
  };

  const takeSnapshot = () => {
    setSnapshotUrl(`${backendUrl}/snapshot?ts=${Date.now()}`);
  };

  return (
    <div className={`app-shell ${theme}`}>
      <div className="container py-4">
        <div className="d-flex justify-content-between align-items-center mb-3">
          <h2 className="mb-0">Smart Vision Voice Navigation</h2>
          <button
            className="btn btn-outline-secondary"
            onClick={() => setTheme(theme === 'light' ? 'dark' : 'light')}
          >
            Toggle {theme === 'light' ? 'Dark' : 'Light'} Theme
          </button>
        </div>

        <div className="mb-3 d-flex gap-2 flex-wrap">
          <button className="btn btn-success" onClick={() => setIsRunning(true)}>Start</button>
          <button className="btn btn-warning" onClick={() => setIsRunning(false)}>Stop</button>
          <button className="btn btn-danger" onClick={resetState}>Reset</button>
          <button className="btn btn-info text-white" onClick={takeSnapshot}>Snapshot</button>
        </div>

        <div className="row g-3">
          <div className="col-lg-8">
            <VideoFeed isRunning={isRunning} backendUrl={backendUrl} />
          </div>
          <div className="col-lg-4 d-grid gap-3">
            <ObjectList objects={objects} />
            <VoiceControl backendUrl={backendUrl} onCommand={setLastCommand} />
            <NavigationPanel feedback={feedback} />
            <div className="card shadow-sm">
              <div className="card-header">Last Voice Command</div>
              <div className="card-body">{lastCommand}</div>
            </div>
          </div>
        </div>

        {snapshotUrl && (
          <div className="mt-4">
            <h5>Latest Snapshot</h5>
            <img src={snapshotUrl} alt="Snapshot" className="img-fluid rounded border" />
          </div>
        )}
      </div>
    </div>
  );
}

export default App;
