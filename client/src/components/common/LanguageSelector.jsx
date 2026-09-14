import React from "react";
import { SUPPORTED_LANGUAGES } from "../../context/LanguageContext";

export default function LanguageSelector({ value = "en", onChange }) {
  return (
    <select
      className="language-select"
      value={value}
      onChange={(event) => onChange?.(event.target.value)}
      aria-label="Select language"
    >
      {Object.entries(SUPPORTED_LANGUAGES).map(([code, label]) => (
        <option key={code} value={code}>
          {label}
        </option>
      ))}
    </select>
  );
}
