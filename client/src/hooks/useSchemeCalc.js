import { useState } from "react";
import { calculateEligibility, getEMISchedule } from "../services/api";

// Encapsulates the two-step calculator flow:
//   1. calculate-eligibility -> scheme, project cost, loan amount
//   2. emi-schedule           -> full quarterly repayment breakdown
// Keeping this in one hook means FinancialCalculator.jsx just renders
// state instead of juggling two API calls and their loading/error states.
export default function useSchemeCalc() {
  const [eligibility, setEligibility] = useState(null);
  const [schedule, setSchedule] = useState(null);
  const [loading, setLoading] = useState(false);
  const [scheduleLoading, setScheduleLoading] = useState(false);
  const [error, setError] = useState("");

  const calculate = async (capital) => {
    setLoading(true);
    setError("");
    setEligibility(null);
    setSchedule(null);
    try {
      const result = await calculateEligibility(capital);
      setEligibility(result);
      return result;
    } catch (err) {
      setError(err.message || "Unable to calculate right now. Please check your connection.");
      return null;
    } finally {
      setLoading(false);
    }
  };

  const loadSchedule = async () => {
    if (!eligibility) return;
    setScheduleLoading(true);
    try {
      const result = await getEMISchedule({
        loanAmount: eligibility.loan_amount,
        interestRate: eligibility.interest_rate,
        tenureYears: eligibility.tenure_years,
        moratoriumMonths: eligibility.moratorium_months,
      });
      setSchedule(result);
    } catch (err) {
      setError(err.message || "Unable to load the repayment schedule.");
    } finally {
      setScheduleLoading(false);
    }
  };

  return { eligibility, schedule, loading, scheduleLoading, error, calculate, loadSchedule };
}
