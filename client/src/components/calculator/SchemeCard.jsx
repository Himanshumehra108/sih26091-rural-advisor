import React from "react";
import { formatCurrency } from "../../utils/formatCurrency";

function SchemeCard({ scheme, interest, tenure, loan, capped, message }) {
  return (
    <div className="scheme-card">
      <div className="scheme-top">
        <div>
          <small>RECOMMENDED SCHEME</small>
          <h2>🏦 {scheme || "Loan Scheme"}</h2>
        </div>
        {capped && <span className="capped-badge">Capped</span>}
      </div>

      <div className="scheme-details">
        <div>
          <span>Loan amount</span>
          <strong>{formatCurrency(loan)}</strong>
        </div>
        <div>
          <span>Interest</span>
          <strong>{interest || "—"}%</strong>
        </div>
        <div>
          <span>Tenure</span>
          <strong>{tenure || "—"} years</strong>
        </div>
      </div>

      {message && <p className="scheme-message">ℹ️ {message}</p>}
    </div>
  );
}

export default SchemeCard;
