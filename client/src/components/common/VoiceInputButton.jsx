import React from "react";
import useSpeechInput from "../../hooks/useSpeechInput";

// Drop this into any text field to let the user speak instead of type —
// used on FeasibilityForm for the location fields. Falls back to a
// disabled, tooltip-explained button on browsers without speech support.
export default function VoiceInputButton({ onTranscript, language = "en-IN" }) {
  const { isListening, isSupported, start, transcript } = useSpeechInput(language);

  React.useEffect(() => {
    if (transcript) onTranscript?.(transcript);
  }, [transcript, onTranscript]);

  if (!isSupported) {
    return (
      <button
        type="button"
        className="voice-button voice-button-disabled"
        disabled
        title="Voice input isn't supported in this browser"
      >
        🎙️
      </button>
    );
  }

  return (
    <button
      type="button"
      className={isListening ? "voice-button listening" : "voice-button"}
      onClick={start}
      title="Speak instead of typing"
    >
      {isListening ? "🎙️ Listening…" : "🎙️"}
    </button>
  );
}
