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
  const [updatedAt, setUpdatedAt] = useState(0);
  const [lastCommand, setLastCommand] = useState('None');
  const [feedback, setFeedback] = useState('');
  const [theme, setTheme] = useState('light');
  const [snapshotUrl, setSnapshotUrl] = useState('');
  const [backendStatus, setBackendStatus] = useState('unknown');
  const [cameraOpen, setCameraOpen] = useState(false);
  const [fps, setFps] = useState(0);
  const [backendError, setBackendError] = useState('');
  const [audioEnabled, setAudioEnabled] = useState(true);

  useEffect(() => {
    if (!isRunning) return undefined;

    const interval = setInterval(async () => {
      try {
        const [objectsRes, statusRes] = await Promise.all([
          axios.get(`${backendUrl}/detect_objects`),
          axios.get(`${backendUrl}/status`)
        ]);

        setObjects(objectsRes.data.objects || []);
        setUpdatedAt(objectsRes.data.updated_at || 0);

        const st = statusRes.data;
        setBackendStatus(st.backend || 'ok');
        setCameraOpen(Boolean(st.detector?.camera_open));
        setFps(st.detector?.fps || 0);
        setBackendError(st.detector?.last_error || '');
        setFeedback(st.last_feedback || '');
      } catch {
        setBackendStatus('offline');
        setBackendError('Backend unreachable. Check Flask server and CORS settings.');
      }
    }, 1000);

    return () => clearInterval(interval);
  }, [isRunning, backendUrl]);

  const speakInBrowser = (text) => {
    if (!audioEnabled || !text) return;
    if (!window.speechSynthesis) return;

    window.speechSynthesis.cancel();
    const utterance = new SpeechSynthesisUtterance(text);
    utterance.lang = 'en-US';
    utterance.rate = 1;
    window.speechSynthesis.speak(utterance);
  };

  const onVoiceResult = (payload) => {
    const newCommand = payload.command || 'None';
    const newFeedback = payload.feedback || '';

    setLastCommand(newCommand);
    setFeedback(newFeedback);
    if (payload.intent?.intent === 'find') {
      setObjects(payload.matched_objects || []);
    } else {
      setObjects(payload.all_objects || []);
    }

    speakInBrowser(newFeedback);
  };

  const resetState = () => {
    setObjects([]);
    setUpdatedAt(0);
    setLastCommand('None');
    setFeedback('');
    setSnapshotUrl('');
    setBackendError('');
    if (window.speechSynthesis) {
      window.speechSynthesis.cancel();
    }
  };

  return (
    <div className={`app-shell ${theme}`}>
      <div className="container py-4">
        <div className="d-flex justify-content-between align-items-center mb-3">
          <h2 className="mb-0">Smart Vision Voice Navigation</h2>
          <div className="d-flex gap-2">
            <button className="btn btn-outline-secondary" onClick={() => setAudioEnabled(!audioEnabled)}>
              Audio: {audioEnabled ? 'On' : 'Off'}
            </button>
            <button className="btn btn-outline-secondary" onClick={() => setTheme(theme === 'light' ? 'dark' : 'light')}>
              Toggle {theme === 'light' ? 'Dark' : 'Light'} Theme
            </button>
          </div>
        </div>

        <div className="status-row mb-3">
          <span className={`badge ${backendStatus === 'ok' ? 'text-bg-success' : 'text-bg-danger'}`}>Backend: {backendStatus}</span>
          <span className={`badge ${cameraOpen ? 'text-bg-success' : 'text-bg-warning'}`}>Camera: {cameraOpen ? 'Connected' : 'Unavailable'}</span>
          <span className="badge text-bg-primary">Detections: {objects.length}</span>
          <span className="badge text-bg-secondary">FPS: {Number(fps).toFixed(1)}</span>
        </div>

        {backendError && <div className="alert alert-warning py-2">{backendError}</div>}

        <div className="mb-3 d-flex gap-2 flex-wrap">
          <button className="btn btn-success" onClick={() => setIsRunning(true)}>Start</button>
          <button className="btn btn-warning" onClick={() => setIsRunning(false)}>Stop</button>
          <button className="btn btn-danger" onClick={resetState}>Reset</button>
          <button className="btn btn-info text-white" onClick={() => setSnapshotUrl(`${backendUrl}/snapshot?ts=${Date.now()}`)}>Snapshot</button>
        </div>

        <div className="row g-3">
          <div className="col-lg-8">
            <VideoFeed isRunning={isRunning} backendUrl={backendUrl} />
          </div>
          <div className="col-lg-4 d-grid gap-3">
            <ObjectList objects={objects} updatedAt={updatedAt} />
            <VoiceControl backendUrl={backendUrl} onResult={onVoiceResult} />
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
