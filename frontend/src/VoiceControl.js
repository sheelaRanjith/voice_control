import React, { useMemo, useState } from 'react';
import axios from 'axios';

function VoiceControl({ backendUrl, onResult }) {
  const [listening, setListening] = useState(false);
  const [error, setError] = useState('');
  const [textCommand, setTextCommand] = useState('find person');
  const [audioFile, setAudioFile] = useState(null);

  const recognition = useMemo(() => {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SpeechRecognition) return null;
    const rec = new SpeechRecognition();
    rec.lang = 'en-US';
    rec.interimResults = false;
    rec.maxAlternatives = 1;
    return rec;
  }, []);

  const sendTextCommand = async (transcript) => {
    try {
      const response = await axios.post(`${backendUrl}/voice_command`, { transcript, language: 'en' });
      onResult(response.data);
      setError('');
    } catch {
      setError('Could not send command to backend.');
    }
  };

  const sendAudioFile = async () => {
    if (!audioFile) {
      setError('Please choose an audio file first.');
      return;
    }

    try {
      const formData = new FormData();
      formData.append('audio', audioFile);
      const response = await axios.post(`${backendUrl}/voice_command`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      onResult(response.data);
      setError('');
    } catch {
      setError('Could not process uploaded audio.');
    }
  };

  const startListening = () => {
    if (!recognition) {
      setError('SpeechRecognition API is not supported in this browser. Use text/audio upload options.');
      return;
    }

    recognition.start();
    setListening(true);
    recognition.onresult = async (event) => {
      const transcript = event.results[0][0].transcript;
      setTextCommand(transcript);
      await sendTextCommand(transcript);
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
            placeholder="find person / find water bottle / navigate left"
          />
          <button className="btn btn-outline-primary" onClick={() => sendTextCommand(textCommand)}>Send</button>
        </div>

        <button className="btn btn-primary" onClick={startListening} disabled={listening}>
          {listening ? 'Listening...' : 'Speak Command'}
        </button>

        <div className="input-group">
          <input
            type="file"
            className="form-control"
            accept="audio/*"
            onChange={(e) => setAudioFile(e.target.files?.[0] || null)}
          />
          <button className="btn btn-outline-secondary" onClick={sendAudioFile}>Upload Audio</button>
        </div>

        <small className="text-muted">Examples: find calendar, find water bottle, detect objects, navigate right.</small>
        {error && <p className="text-danger mb-0">{error}</p>}
      </div>
    </div>
  );
}

export default VoiceControl;
