import React from 'react';

export default function VoiceInputButton({ onTranscript }) {
  return <button type="button" onClick={() => onTranscript?.('')}>Voice input</button>;
}
