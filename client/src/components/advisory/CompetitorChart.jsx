import React from "react";

const SATURATION_LEVELS = { low: 33, medium: 66, high: 100 };

export default function CompetitorChart({ competitorDensity }) {
  if (!competitorDensity) return null;
  const { estimated_count, saturation_level } = competitorDensity;
  const fill = SATURATION_LEVELS[saturation_level] ?? 50;

  return (
    <section className="competitor-card" aria-label="Competitor density">
      <div className="competitor-count">
        <strong>{estimated_count ?? "—"}</strong>
        <span>competitors nearby</span>
      </div>

      <div className="saturation-bar">
        <div
          className={`saturation-fill saturation-${saturation_level || "medium"}`}
          style={{ width: `${fill}%` }}
        />
      </div>
      <small className="saturation-label">
        Market saturation: {saturation_level || "unknown"}
      </small>
    </section>
  );
}
