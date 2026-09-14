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

function FinancialCalculator() {
  const [capital, setCapital] = useState("");
  const [inputError, setInputError] = useState("");

  const { eligibility, schedule, loading, scheduleLoading, error, calculate, loadSchedule } =
    useSchemeCalc();

  const handleCalculate = async () => {
    if (!isPositiveNumber(capital)) {
      setInputError("Please enter a valid amount.");
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
          <div className="page-badge">💰 FINANCIAL CALCULATOR</div>
          <h1>How much can you borrow?</h1>
          <p>Enter the money you can invest yourself. We'll calculate your possible project size and loan.</p>
        </div>

        <section className="calculator-container">
          <div className="input-panel">
            <label>Your available money</label>
            <MarginInput value={capital} onChange={setCapital} />
            <p className="input-help">This is the amount you can contribute yourself (your margin).</p>

            {displayError && <div className="error-message">⚠️ {displayError}</div>}

            <button className="calculate-button" onClick={handleCalculate} disabled={loading}>
              {loading ? "Calculating…" : "Calculate my loan →"}
            </button>
          </div>

          {!eligibility && !loading && (
            <div className="empty-result">
              <div className="empty-icon">💡</div>
              <h3>Your result will appear here</h3>
              <p>Enter your available capital and click calculate to see your funding potential.</p>
            </div>
          )}

          {loading && (
            <div className="empty-result">
              <Loader label="Calculating your options…" />
            </div>
          )}

          {eligibility && (
            <div className="calculator-result">
              <div className="result-title">
                <span>YOUR FUNDING POTENTIAL</span>
                <h2>Here's what your money could unlock.</h2>
              </div>

              <div className="result-grid">
                <div className="result-card highlight">
                  <span>🏗️ Possible project</span>
                  <strong>{formatCurrency(eligibility.project_cost)}</strong>
                </div>
                <div className="result-card">
                  <span>🏦 Possible loan</span>
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
                  {scheduleLoading ? "Loading schedule…" : "📅 View detailed repayment schedule"}
                </button>
              )}

              {schedule && (
                <div className="schedule-panel">
                  <div className="result-grid">
                    <div className="result-card">
                      <span>Quarterly EMI</span>
                      <strong>{formatCurrency(schedule.quarterly_emi)}</strong>
                    </div>
                    <div className="result-card">
                      <span>Total interest</span>
                      <strong>{formatCurrency(schedule.total_interest)}</strong>
                    </div>
                    <div className="result-card">
                      <span>Total repayment</span>
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
                <summary>Developer: view API response</summary>
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
