import React from "react";
import { useLanguage } from "../../context/LanguageContext";

const SATURATION_LEVELS = { low: 33, medium: 66, high: 100 };

export default function CompetitorChart({ competitorDensity }) {
  const { t } = useLanguage();
  if (!competitorDensity) return null;
  const { estimated_count, saturation_level } = competitorDensity;
  const fill = SATURATION_LEVELS[saturation_level] ?? 50;

  return (
    <section className="competitor-card" aria-label={t("competitors.aria")}>
      <div className="competitor-count">
        <strong>{estimated_count ?? "—"}</strong>
        <span>{t("competitors.nearby")}</span>
      </div>

      <div className="saturation-bar">
        <div
          className={`saturation-fill saturation-${saturation_level || "medium"}`}
          style={{ width: `${fill}%` }}
        />
      </div>
      <small className="saturation-label">
        {t("competitors.saturation", { level: t(`competitors.${saturation_level || "unknown"}`) })}
      </small>
    </section>
  );
}
