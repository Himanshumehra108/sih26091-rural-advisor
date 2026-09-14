import React from "react";

// No real map library is wired in (backend's geo_service.py is a stub
// returning no places yet), so this renders a clear stat summary
// instead of faking a map that has no real data behind it.
export default function MarketReachMap({ marketReach }) {
  if (!marketReach) return null;
  const { radius_km, estimated_consumer_base, distribution_channels = [] } = marketReach;

  return (
    <section className="market-reach-card" aria-label="Market reach">
      <div className="market-reach-radius">
        <div className="radius-ring">
          <strong>{radius_km ?? "—"}</strong>
          <small>km radius</small>
        </div>
      </div>

      <div className="market-reach-stats">
        <div>
          <span>Estimated reach</span>
          <strong>
            {estimated_consumer_base ? estimated_consumer_base.toLocaleString("en-IN") : "—"} people
          </strong>
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
