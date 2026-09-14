import React, { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import Navbar from "../components/common/Navbar";
import Loader from "../components/common/Loader";
import { useAuth } from "../context/AuthContext";
import { listReports } from "../services/api";

export default function Dashboard() {
  const { isAuthenticated, user } = useAuth();
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
        if (!cancelled) setError(err.message || "Couldn't load your saved reports.");
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
          <div className="page-badge">📊 YOUR REPORTS</div>
          <h1>{isAuthenticated ? `Welcome back, ${user?.name}` : "Saved reports"}</h1>
          <p>Every feasibility report you save shows up here.</p>
        </div>

        {loading && (
          <div className="empty-result">
            <Loader label="Loading your reports…" />
          </div>
        )}

        {!loading && error && (
          <div className="empty-result">
            <div className="empty-icon">⚠️</div>
            <h3>Couldn't load reports</h3>
            <p>{error}</p>
          </div>
        )}

        {!loading && !error && reports.length === 0 && (
          <div className="empty-result">
            <div className="empty-icon">📊</div>
            <h3>No saved reports yet</h3>
            <p>Generate a feasibility report and save it to see it here.</p>
            <Link to="/feasibility" className="primary-button">
              Check my business →
            </Link>
          </div>
        )}

        {!loading && reports.length > 0 && (
          <section className="report-grid">
            {reports.map((report, i) => (
              <div key={i} className="report-card">
                <div className="report-icon">📄</div>
                <h3>{report._meta?.businessCategory || report.business_category || "Report"}</h3>
                <p>{report.opportunity_analysis || "Saved report"}</p>
              </div>
            ))}
          </section>
        )}
      </main>
    </>
  );
}
