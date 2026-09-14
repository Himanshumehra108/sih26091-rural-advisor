import React from "react";

const QUADRANTS = [
  { key: "strengths", title: "Strengths", icon: "💪", className: "swot-strengths" },
  { key: "weaknesses", title: "Weaknesses", icon: "⚠️", className: "swot-weaknesses" },
  { key: "opportunities", title: "Opportunities", icon: "🚀", className: "swot-opportunities" },
  { key: "threats", title: "Threats", icon: "🛑", className: "swot-threats" },
];

// Renders the full 2x2 SWOT grid from the backend's `swot` object:
// { strengths: [], weaknesses: [], opportunities: [], threats: [] }
export default function SWOTCard({ swot }) {
  if (!swot) return null;

  return (
    <div className="swot-grid">
      {QUADRANTS.map(({ key, title, icon, className }) => (
        <div key={key} className={`swot-quadrant ${className}`}>
          <h3>
            {icon} {title}
          </h3>
          <ul>
            {(swot[key] || []).length > 0 ? (
              swot[key].map((item, i) => <li key={i}>{item}</li>)
            ) : (
              <li className="swot-empty">Nothing flagged here.</li>
            )}
          </ul>
        </div>
      ))}
    </div>
  );
}
