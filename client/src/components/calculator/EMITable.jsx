import React from "react";
import { formatCurrency } from "../../utils/formatCurrency";
import { useLanguage } from "../../context/LanguageContext";

// Renders the exact schedule array returned by
// POST /api/v1/calculator/emi-schedule: one row per quarter, each with
// { quarter, phase, principal_paid, interest_paid, emi, balance }.
export default function EMITable({ schedule = [] }) {
  const { t } = useLanguage();
  if (schedule.length === 0) return null;

  return (
    <div className="emi-table-wrapper">
      <table className="emi-table">
        <thead>
          <tr>
            <th>{t("emi.quarter")}</th>
            <th>{t("emi.phase")}</th>
            <th>{t("emi.principal")}</th>
            <th>{t("emi.interest")}</th>
            <th>{t("emi.emi")}</th>
            <th>{t("emi.balance")}</th>
          </tr>
        </thead>
        <tbody>
          {schedule.map((row) => (
            <tr key={row.quarter} className={row.phase === "moratorium" ? "moratorium-row" : ""}>
              <td>Q{row.quarter}</td>
              <td className="phase-cell">{row.phase}</td>
              <td>{row.principal_paid ? formatCurrency(row.principal_paid) : "—"}</td>
              <td>{row.interest_paid ? formatCurrency(row.interest_paid) : "—"}</td>
              <td>{row.emi ? formatCurrency(row.emi) : "—"}</td>
              <td>{formatCurrency(row.balance)}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
