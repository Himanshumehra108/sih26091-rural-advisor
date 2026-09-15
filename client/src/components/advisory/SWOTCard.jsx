import React from "react";
import { useLanguage } from "../../context/LanguageContext";

const QUADRANTS = [
  { key: "strengths", title: "Strengths", icon: "💪", className: "swot-strengths" },
  { key: "weaknesses", title: "Weaknesses", icon: "⚠️", className: "swot-weaknesses" },
  { key: "opportunities", title: "Opportunities", icon: "🚀", className: "swot-opportunities" },
  { key: "threats", title: "Threats", icon: "🛑", className: "swot-threats" },
];

// Renders the full 2x2 SWOT grid from the backend's `swot` object:
// { strengths: [], weaknesses: [], opportunities: [], threats: [] }
export default function SWOTCard({ swot }) {
  const { t } = useLanguage();
  if (!swot) return null;

  return (
    <div className="swot-grid">
      {QUADRANTS.map(({ key, icon, className }) => (
        <div key={key} className={`swot-quadrant ${className}`}>
          <h3>
            {icon} {t(`swot.${key}`)}
          </h3>
          <ul>
            {(swot[key] || []).length > 0 ? (
              swot[key].map((item, i) => <li key={i}>{item}</li>)
            ) : (
              <li className="swot-empty">{t("swot.empty")}</li>
            )}
          </ul>
        </div>
      ))}
    </div>
  );
}
