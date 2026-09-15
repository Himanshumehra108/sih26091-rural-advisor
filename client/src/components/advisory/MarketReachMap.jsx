import React from "react";
import { useLanguage } from "../../context/LanguageContext";

// No real map library is wired in (backend's geo_service.py is a stub
// returning no places yet), so this renders a clear stat summary
// instead of faking a map that has no real data behind it.
export default function MarketReachMap({ marketReach }) {
  const { t } = useLanguage();
  if (!marketReach) return null;
  const {
    radius_km,
    estimated_consumer_base,
    population,
    distribution_channels = [],
  } = marketReach;
  const populationData = population || {
    population: estimated_consumer_base,
    population_level: estimated_consumer_base ? "unknown" : null,
    area_name: null,
    source: null,
    year: null,
    status: estimated_consumer_base ? "success" : "unavailable",
  };
  const hasPopulation = populationData.status === "success" && populationData.population != null;

  return (
    <section className="market-reach-card" aria-label={t("market.aria")}>
      <div className="market-reach-radius">
        <div className="radius-ring">
          <strong>{radius_km ?? "—"}</strong>
          <small>{t("market.kmRadius")}</small>
        </div>
      </div>

      <div className="market-reach-stats">
        <div>
          <span>{t("market.population")}</span>
          <strong>
            {hasPopulation ? populationData.population.toLocaleString("en-IN") : t("market.populationUnavailable")}
          </strong>
          <small>
            {hasPopulation ? (
              <>{populationData.area_name ? `${populationData.area_name} · ` : ""}{t(`market.populationLevel.${populationData.population_level}`)}{populationData.year ? ` · ${t("market.dataYear", { year: populationData.year })}` : ""}</>
            ) : t("market.populationUnavailableDetail")}
          </small>
          {hasPopulation && populationData.source && <small>{t("market.source", { source: populationData.source })}</small>}
        </div>

        {distribution_channels.length > 0 && (
          <div className="channel-tags">
            {distribution_channels.map((channel) => (
              <span key={channel} className="channel-tag">
                {channel}
              </span>
            ))}
          </div>
        )}
      </div>
    </section>
  );
}
