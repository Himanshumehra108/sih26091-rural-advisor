import React from "react";
import { formatCurrency } from "../../utils/formatCurrency";
import { useLanguage } from "../../context/LanguageContext";

function SchemeCard({ scheme, interest, tenure, loan, capped, message }) {
  const { t } = useLanguage();
  return (
    <div className="scheme-card">
      <div className="scheme-top">
        <div>
          <small>{t("scheme.recommended")}</small>
          <h2>🏦 {scheme || t("scheme.loanScheme")}</h2>
        </div>
        {capped && <span className="capped-badge">{t("scheme.capped")}</span>}
      </div>

      <div className="scheme-details">
        <div>
          <span>{t("scheme.loanAmount")}</span>
          <strong>{formatCurrency(loan)}</strong>
        </div>
        <div>
          <span>{t("scheme.interest")}</span>
          <strong>{interest || "—"}%</strong>
        </div>
        <div>
          <span>{t("scheme.tenure")}</span>
          <strong>{tenure || "—"} {t("common.years", { count: "" }).trim()}</strong>
        </div>
      </div>

      {message && <p className="scheme-message">ℹ️ {message}</p>}
    </div>
  );
}

export default SchemeCard;
