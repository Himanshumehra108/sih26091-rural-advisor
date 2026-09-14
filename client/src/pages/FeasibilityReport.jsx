import React, { useState } from "react";
import { Link } from "react-router-dom";
import Navbar from "../components/common/Navbar";
import SWOTCard from "../components/advisory/SWOTCard";
import MarketReachMap from "../components/advisory/MarketReachMap";
import CompetitorChart from "../components/advisory/CompetitorChart";
import PricingSuggestion from "../components/advisory/PricingSuggestion";
import { saveReport } from "../services/api";

function FeasibilityReport() {
  const stored = sessionStorage.getItem("feasibilityReport");
  const report = stored ? JSON.parse(stored) : null;

  const [saveState, setSaveState] = useState("idle"); // idle | saving | saved | error

  if (!report) {
    return (
      <>
        <Navbar />
        <main className="page">
          <div className="empty-result">
            <div className="empty-icon">📊</div>
            <h2>No report found</h2>
            <p>Generate a feasibility report first.</p>
            <Link to="/feasibility" className="primary-button">
              Create report →
            </Link>
          </div>
        </main>
      </>
    );
  }

  const { market_reach, opportunity_analysis, swot, competitor_density, pricing_suggestion, _meta } = report;

  const handleSave = async () => {
    // NOTE: server/app/api/v1/routes_reports.py exists but is not yet
    // registered in main.py — this call will 404 until that's wired up
    // backend-side. See INTEGRATION_NOTES.md.
    try {
      setSaveState("saving");
      await saveReport({ ...report });
      setSaveState("saved");
    } catch {
      setSaveState("error");
    }
  };

  return (
    <>
      <Navbar />

      <main className="page report-page">
        <div className="report-header">
          <div>
            <div className="page-badge">FEASIBILITY REPORT</div>
            <h1>{_meta?.businessCategory || "Your Business"}</h1>
            <p>
              📍 {[_meta?.location?.village, _meta?.location?.block, _meta?.location?.district, _meta?.location?.state]
                .filter(Boolean)
                .join(", ") || "Your location"}
            </p>
          </div>

          <button
            className="secondary-button save-report-button"
            onClick={handleSave}
            disabled={saveState === "saving" || saveState === "saved"}
          >
            {saveState === "saved" ? "✅ Saved" : saveState === "saving" ? "Saving…" : "💾 Save report"}
          </button>
        </div>

        {saveState === "error" && (
          <div className="error-message">
            ⚠️ Couldn't save this report right now — the reports endpoint may not be
            enabled on the backend yet.
          </div>
        )}

        <section className="large-report-card">
          <div className="card-heading">
            <span>💡</span>
            <div>
              <small>MARKET INSIGHT</small>
              <h2>What looks promising?</h2>
            </div>
          </div>
          <p>{opportunity_analysis || "Your opportunity analysis will appear here."}</p>
        </section>

        <section className="report-grid">
          <MarketReachMap marketReach={market_reach} />
          <CompetitorChart competitorDensity={competitor_density} />
          <PricingSuggestion pricing={pricing_suggestion} />
        </section>

        <section className="large-report-card">
          <div className="card-heading">
            <span>🧭</span>
            <div>
              <small>SWOT</small>
              <h2>A full picture, at a glance</h2>
            </div>
          </div>
          <SWOTCard swot={swot} />
        </section>

        <details className="debug-response">
          <summary>Developer: view complete API response</summary>
          <pre>{JSON.stringify(report, null, 2)}</pre>
        </details>
      </main>
    </>
  );
}

export default FeasibilityReport;
