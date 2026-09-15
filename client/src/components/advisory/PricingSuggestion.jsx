import React from "react";
import { useLanguage } from "../../context/LanguageContext";

export default function PricingSuggestion({ pricing }) {
  const { t } = useLanguage();
  if (!pricing) return null;
  const { suggested_price_range, reasoning } = pricing;

  return (
    <section className="pricing-card" aria-label={t("pricing.aria")}>
      <div className="pricing-range">{suggested_price_range || "—"}</div>
      <p>{reasoning}</p>
    </section>
  );
}
