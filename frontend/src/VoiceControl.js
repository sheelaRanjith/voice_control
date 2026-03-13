import React, { useMemo, useState } from 'react';
import axios from 'axios';

function VoiceControl({ backendUrl, onCommand }) {
  const [listening, setListening] = useState(false);
  const [error, setError] = useState('');

  const recognition = useMemo(() => {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SpeechRecognition) {
      return null;
    }
    const rec = new SpeechRecognition();
    rec.lang = 'en-US';
    rec.interimResults = false;
    rec.maxAlternatives = 1;
    return rec;
  }, []);

  const startListening = () => {
    if (!recognition) {
      setError('SpeechRecognition API is not supported in this browser.');
      return;
    }

    setError('');
    recognition.start();
    setListening(true);

    recognition.onresult = async (event) => {
      const transcript = event.results[0][0].transcript;
      try {
        const response = await axios.post(`${backendUrl}/voice_command`, { transcript });
        onCommand(response.data.command);
      } catch {
        setError('Could not send voice command to backend.');
      }
    };

    recognition.onerror = () => {
      setError('Voice recognition failed. Try again.');
    };

    recognition.onend = () => {
      setListening(false);
    };
  };

  return (
    <div className="card shadow-sm h-100">
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
