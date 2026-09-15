import React, { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import Navbar from "../components/common/Navbar";
import Loader from "../components/common/Loader";
import { useAuth } from "../context/AuthContext";
import { listReports } from "../services/api";
import { useLanguage } from "../context/LanguageContext";

export default function Dashboard() {
  const { isAuthenticated, user } = useAuth();
  const { t } = useLanguage();
  const [reports, setReports] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    // NOTE: server/app/api/v1/routes_reports.py exists but isn't
    // registered in main.py yet — this will 404 until that's fixed.
    // See INTEGRATION_NOTES.md.
    let cancelled = false;
    (async () => {
      try {
        const data = await listReports();
        if (!cancelled) setReports(Array.isArray(data) ? data : []);
      } catch (err) {
        if (!cancelled) setError(err.message || t("dashboard.loadFailed"));
      } finally {
        if (!cancelled) setLoading(false);
      }
    })();
    return () => {
      cancelled = true;
    };
  }, []);

  return (
    <>
      <Navbar />
      <main className="page">
        <div className="page-header">
          <div className="page-badge">📊 {t("dashboard.badge")}</div>
          <h1>{isAuthenticated ? t("dashboard.welcomeBack", { name: user?.name }) : t("dashboard.savedReports")}</h1>
          <p>{t("dashboard.subtitle")}</p>
        </div>

        {loading && (
          <div className="empty-result">
            <Loader label={t("dashboard.loading")} />
          </div>
        )}

        {!loading && error && (
          <div className="empty-result">
            <div className="empty-icon">⚠️</div>
            <h3>{t("dashboard.loadFailedTitle")}</h3>
            <p>{error}</p>
          </div>
        )}

        {!loading && !error && reports.length === 0 && (
          <div className="empty-result">
            <div className="empty-icon">📊</div>
            <h3>{t("dashboard.emptyTitle")}</h3>
            <p>{t("dashboard.emptyBody")}</p>
            <Link to="/feasibility" className="primary-button">
              {t("dashboard.checkBusiness")}
            </Link>
          </div>
        )}

        {!loading && reports.length > 0 && (
          <section className="report-grid">
            {reports.map((report, i) => (
              <div key={i} className="report-card">
                <div className="report-icon">📄</div>
                <h3>{report._meta?.businessCategory || report.business_category || t("common.report")}</h3>
                <p>{report.opportunity_analysis || t("common.savedReport")}</p>
              </div>
            ))}
          </section>
        )}
      </main>
    </>
  );
}
