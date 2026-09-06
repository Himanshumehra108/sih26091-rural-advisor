import React from 'react';

export default function LanguageSelector({ value = 'en', onChange }) {
  return (
    <select value={value} onChange={(event) => onChange?.(event.target.value)} aria-label="Language">
      <option value="en">English</option>
      <option value="hi">Hindi</option>
    </select>
  );
}
