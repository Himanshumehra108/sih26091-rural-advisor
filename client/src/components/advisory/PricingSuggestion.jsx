import React from "react";

export default function PricingSuggestion({ pricing }) {
  if (!pricing) return null;
  const { suggested_price_range, reasoning } = pricing;

  return (
    <section className="pricing-card" aria-label="Pricing suggestion">
      <div className="pricing-range">{suggested_price_range || "—"}</div>
      <p>{reasoning}</p>
    </section>
  );
}
