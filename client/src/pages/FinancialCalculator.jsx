import React, { useState } from "react";
import Navbar from "../components/common/Navbar";
import MarginInput from "../components/calculator/MarginInput";
import SchemeCard from "../components/calculator/SchemeCard";
import EMITable from "../components/calculator/EMITable";
import MoratoriumTimeline from "../components/calculator/MoratoriumTimeline";
import Loader from "../components/common/Loader";
import useSchemeCalc from "../hooks/useSchemeCalc";
import { formatCurrency } from "../utils/formatCurrency";
import { isPositiveNumber } from "../utils/validators";
import { useLanguage } from "../context/LanguageContext";

function FinancialCalculator() {
  const [capital, setCapital] = useState("");
  const [inputError, setInputError] = useState("");
  const { t } = useLanguage();

  const { eligibility, schedule, loading, scheduleLoading, error, calculate, loadSchedule } =
    useSchemeCalc();

  const handleCalculate = async () => {
    if (!isPositiveNumber(capital)) {
      setInputError(t("calculator.invalidAmount"));
      return;
    }
    setInputError("");
    await calculate(capital);
  };

  const displayError = inputError || error;

  return (
    <>
      <Navbar />

      <main className="page">
        <div className="page-header">
          <div className="page-badge">💰 {t("calculator.badge")}</div>
          <h1>{t("calculator.title")}</h1>
          <p>{t("calculator.subtitle")}</p>
        </div>

        <section className="calculator-container">
          <div className="input-panel">
            <label>{t("calculator.availableMoney")}</label>
            <MarginInput value={capital} onChange={setCapital} />
            <p className="input-help">{t("calculator.help")}</p>

            {displayError && <div className="error-message">⚠️ {displayError}</div>}

            <button className="calculate-button" onClick={handleCalculate} disabled={loading}>
              {loading ? t("calculator.calculating") : t("calculator.calculate")}
            </button>
          </div>

          {!eligibility && !loading && (
            <div className="empty-result">
              <div className="empty-icon">💡</div>
              <h3>{t("calculator.emptyTitle")}</h3>
              <p>{t("calculator.emptyBody")}</p>
            </div>
          )}

          {loading && (
            <div className="empty-result">
              <Loader label={t("calculator.calculatingOptions")} />
            </div>
          )}

          {eligibility && (
            <div className="calculator-result">
              <div className="result-title">
                <span>{t("calculator.fundingPotential")}</span>
                <h2>{t("calculator.unlock")}</h2>
              </div>

              <div className="result-grid">
                <div className="result-card highlight">
                  <span>🏗️ {t("calculator.possibleProject")}</span>
                  <strong>{formatCurrency(eligibility.project_cost)}</strong>
                </div>
                <div className="result-card">
                  <span>🏦 {t("calculator.possibleLoan")}</span>
                  <strong>{formatCurrency(eligibility.loan_amount)}</strong>
                </div>
              </div>

              <SchemeCard
                scheme={eligibility.scheme_name}
                loan={eligibility.loan_amount}
                interest={eligibility.interest_rate}
                tenure={eligibility.tenure_years}
                capped={eligibility.capped}
                message={eligibility.message}
              />

              {!schedule && (
                <button
                  className="secondary-button"
                  onClick={loadSchedule}
                  disabled={scheduleLoading}
                >
                  {scheduleLoading ? t("calculator.loadingSchedule") : `📅 ${t("calculator.viewSchedule")}`}
                </button>
              )}

              {schedule && (
                <div className="schedule-panel">
                  <div className="result-grid">
                    <div className="result-card">
                      <span>{t("calculator.quarterlyEmi")}</span>
                      <strong>{formatCurrency(schedule.quarterly_emi)}</strong>
                    </div>
                    <div className="result-card">
                      <span>{t("calculator.totalInterest")}</span>
                      <strong>{formatCurrency(schedule.total_interest)}</strong>
                    </div>
                    <div className="result-card">
                      <span>{t("calculator.totalRepayment")}</span>
                      <strong>{formatCurrency(schedule.total_repayment)}</strong>
                    </div>
                  </div>

                  <MoratoriumTimeline
                    moratoriumQuarters={schedule.moratorium_quarters}
                    repaymentQuarters={schedule.repayment_quarters}
                  />

                  <EMITable schedule={schedule.schedule} />
                </div>
              )}

              <details className="debug-response">
                <summary>{t("common.developerApi")}</summary>
                <pre>{JSON.stringify({ eligibility, schedule }, null, 2)}</pre>
              </details>
            </div>
          )}
        </section>
      </main>
    </>
  );
}

export default FinancialCalculator;
