import React, { useMemo, useState } from 'react';
import axios from 'axios';

function VoiceControl({ backendUrl, onResult }) {
  const [listening, setListening] = useState(false);
  const [error, setError] = useState('');
  const [textCommand, setTextCommand] = useState('find person');

  const recognition = useMemo(() => {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SpeechRecognition) return null;
    const rec = new SpeechRecognition();
    rec.lang = 'en-US';
    rec.interimResults = false;
    rec.maxAlternatives = 1;
    return rec;
  }, []);

  const sendCommand = async (transcript) => {
    try {
      const response = await axios.post(`${backendUrl}/voice_command`, { transcript, language: 'en' });
      onResult(response.data);
      setError('');
    } catch {
      setError('Could not send command to backend.');
    }
  };

  const startListening = () => {
    if (!recognition) {
      setError('SpeechRecognition API is not supported in this browser. Use text command input.');
      return;
    }

    recognition.start();
    setListening(true);
    recognition.onresult = async (event) => {
      const transcript = event.results[0][0].transcript;
      setTextCommand(transcript);
      await sendCommand(transcript);
    };
    recognition.onerror = () => setError('Voice recognition failed. Try again.');
    recognition.onend = () => setListening(false);
  };

  return (
    <div className="card shadow-sm h-100">
      <div className="card-header">Voice Command</div>
      <div className="card-body d-grid gap-2">
        <div className="input-group">
          <input
            className="form-control"
            value={textCommand}
            onChange={(e) => setTextCommand(e.target.value)}
            placeholder="find person / detect objects / navigate left"
          />
          <button className="btn btn-outline-primary" onClick={() => sendCommand(textCommand)}>Send</button>
        </div>

        <button className="btn btn-primary" onClick={startListening} disabled={listening}>
          {listening ? 'Listening...' : 'Speak Command'}
        </button>

        <small className="text-muted">Examples: find chair, detect objects, navigate right.</small>
        {error && <p className="text-danger mb-0">{error}</p>}
      <div className="card-header">Voice Command Status</div>
      <div className="card-body">
        <button className="btn btn-primary" onClick={startListening} disabled={listening}>
          {listening ? 'Listening...' : 'Speak Command'}
        </button>
        {error && <p className="text-danger mt-2 mb-0">{error}</p>}
      </div>
    </div>
  );
}

export default VoiceControl;
