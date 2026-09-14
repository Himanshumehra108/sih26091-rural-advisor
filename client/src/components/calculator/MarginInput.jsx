import React from "react";

// Styled to match the app's `.money-input` convention (₹ prefix) so it
// can be dropped into any page needing a capital/margin amount field.
export default function MarginInput({ value, onChange, placeholder = "1,00,000" }) {
  return (
    <div className="money-input">
      <span>₹</span>
      <input
        type="number"
        min="0"
        value={value ?? ""}
        onChange={(event) => onChange?.(event.target.value)}
        placeholder={placeholder}
      />
    </div>
  );
}
