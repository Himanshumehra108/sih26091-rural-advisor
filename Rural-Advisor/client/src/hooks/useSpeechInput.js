import { useState } from 'react';

export default function useSpeechInput() {
  const [transcript, setTranscript] = useState('');
  return { transcript, setTranscript, isSupported: typeof window !== 'undefined' && 'SpeechRecognition' in window };
}
