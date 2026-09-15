import React, { useState } from "react";
import { Link } from "react-router-dom";
import Navbar from "../components/common/Navbar";
import SWOTCard from "../components/advisory/SWOTCard";
import MarketReachMap from "../components/advisory/MarketReachMap";
import CompetitorChart from "../components/advisory/CompetitorChart";
import PricingSuggestion from "../components/advisory/PricingSuggestion";
import { saveReport } from "../services/api";
import { useLanguage } from "../context/LanguageContext";

function FeasibilityReport() {
  const { t } = useLanguage();
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
            <h2>{t("report.noReport")}</h2>
            <p>{t("report.generateFirst")}</p>
            <Link to="/feasibility" className="primary-button">
              {t("report.createReport")}
            </Link>
          </div>
        </main>
      </>
    );
  }

  const { market_reach, opportunity_analysis, swot, competitor_density, pricing_suggestion, _meta } = report;

  const handleSave = async () => {
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
            <div className="page-badge">{t("report.badge")}</div>
            <h1>{_meta?.businessCategory || "Your Business"}</h1>
            <p>
              📍 {[_meta?.location?.village, _meta?.location?.block, _meta?.location?.district, _meta?.location?.state]
                .filter(Boolean)
                .join(", ") || t("report.yourLocation")}
            </p>
          </div>

          <button
            className="secondary-button save-report-button"
            onClick={handleSave}
            disabled={saveState === "saving" || saveState === "saved"}
          >
            {saveState === "saved" ? `✅ ${t("report.saved")}` : saveState === "saving" ? t("report.saving") : `💾 ${t("report.saveReport")}`}
          </button>
        </div>

        {saveState === "error" && (
          <div className="error-message">
            ⚠️ {t("report.saveError")}
          </div>
        )}

        <section className="large-report-card">
          <div className="card-heading">
            <span>💡</span>
            <div>
              <small>{t("report.marketInsight")}</small>
              <h2>{t("report.promising")}</h2>
            </div>
          </div>
          <p>{opportunity_analysis || t("report.opportunityFallback")}</p>
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
              <small>{t("report.swot")}</small>
              <h2>{t("report.fullPicture")}</h2>
            </div>
          </div>
          <SWOTCard swot={swot} />
        </section>

        <details className="debug-response">
          <summary>{t("common.developerCompleteApi")}</summary>
          <pre>{JSON.stringify(report, null, 2)}</pre>
        </details>
      </main>
    </>
  );
}

export default FeasibilityReport;
