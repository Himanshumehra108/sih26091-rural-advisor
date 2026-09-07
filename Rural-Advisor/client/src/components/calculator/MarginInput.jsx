import React from 'react';

export default function MarginInput({ value, onChange }) {
  return <input type="number" min="0" value={value ?? ''} onChange={(event) => onChange?.(event.target.value)} placeholder="Available capital" />;
}
