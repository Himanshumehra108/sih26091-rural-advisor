import { useCallback, useRef, useState } from "react";

// Wraps the browser's native Web Speech API (SpeechRecognition).
// This works independently of the backend — Bhashini's transcribe_audio
// is still a stub server-side, so this hook is what actually powers
// voice input today. Swap it for a Bhashini call once that's real if
// you need language coverage the browser API doesn't support.
export default function useSpeechInput(language = "en-IN") {
  const [transcript, setTranscript] = useState("");
  const [isListening, setIsListening] = useState(false);
  const recognitionRef = useRef(null);

  const isSupported =
    typeof window !== "undefined" &&
    ("SpeechRecognition" in window || "webkitSpeechRecognition" in window);

  const start = useCallback(() => {
    if (!isSupported) return;
    const SpeechRecognition =
      window.SpeechRecognition || window.webkitSpeechRecognition;
    const recognition = new SpeechRecognition();
    recognition.lang = language;
    recognition.interimResults = false;
    recognition.maxAlternatives = 1;

    recognition.onresult = (event) => {
      const text = event.results[0][0].transcript;
      setTranscript(text);
    };
    recognition.onend = () => setIsListening(false);
    recognition.onerror = () => setIsListening(false);

    recognitionRef.current = recognition;
    setIsListening(true);
    recognition.start();
  }, [isSupported, language]);

  const stop = useCallback(() => {
    recognitionRef.current?.stop();
    setIsListening(false);
  }, []);

  return { transcript, setTranscript, isListening, isSupported, start, stop };
}
