import axios from "axios";

// -----------------------------------------------------------------------
// Base client
// -----------------------------------------------------------------------
// The backend wraps every response as { success, data, error }.
// Every function below unwraps that envelope so the rest of the app
// (pages, components) only ever deals with plain data — no page should
// ever need to reach into `.data.data`.
// -----------------------------------------------------------------------

const api = axios.create({
  baseURL: process.env.REACT_APP_API_URL || "http://localhost:8000",
  headers: {
    "Content-Type": "application/json",
  },
});

// Surfaces FastAPI's validation error detail (422) as a readable string
// instead of a generic "Request failed with status code 422".
api.interceptors.response.use(
  (response) => response,
  (error) => {
    const detail = error?.response?.data?.detail;
    if (detail) {
      const message = Array.isArray(detail)
        ? detail.map((d) => d.msg).join(", ")
        : String(detail);
      return Promise.reject(new Error(message));
    }
    return Promise.reject(error);
  }
);

function unwrap(response) {
  const body = response.data;
  // Backend envelope: { success, data, error }
  if (body && typeof body === "object" && "data" in body && "success" in body) {
    if (!body.success) {
      throw new Error(body.error || "Request failed.");
    }
    return body.data;
  }
  // Some routes (auth/status, reports) return plain JSON, no envelope.
  return body;
}

// -----------------------------------------------------------------------
// Calculator — matches server/app/api/v1/routes_calculator.py exactly
// -----------------------------------------------------------------------

// Backend: EligibilityRequest { available_margin: float > 0 }
export const calculateEligibility = async (availableMargin) => {
  const response = await api.post("/api/v1/calculator/calculate-eligibility", {
    available_margin: Number(availableMargin),
  });
  return unwrap(response);
  // -> { scheme_name, project_cost, loan_amount, interest_rate,
  //      tenure_years, moratorium_months, capped, message? }
};

// Backend: EMIRequest { loan_amount, interest_rate, tenure_years, moratorium_months }
export const getEMISchedule = async ({
  loanAmount,
  interestRate,
  tenureYears,
  moratoriumMonths,
}) => {
  const response = await api.post("/api/v1/calculator/emi-schedule", {
    loan_amount: Number(loanAmount),
    interest_rate: Number(interestRate),
    tenure_years: Number(tenureYears),
    moratorium_months: Number(moratoriumMonths),
  });
  return unwrap(response);
  // -> { quarterly_emi, moratorium_quarters, repayment_quarters,
  //      principal_after_moratorium, moratorium_interest_capitalized,
  //      total_interest, total_repayment, schedule: [...] }
};

// -----------------------------------------------------------------------
// Advisory — matches server/app/api/v1/routes_advisory.py exactly
// -----------------------------------------------------------------------

// Backend: FeasibilityRequest {
//   location: { village, block, district, state },
//   available_margin, business_category, language
// }
export const getFeasibilityReport = async ({
  businessCategory,
  location,
  availableMargin,
  language = "en",
}) => {
  const response = await api.post("/api/v1/advisory/feasibility-report", {
    business_category: businessCategory,
    location: {
      village: location.village,
      block: location.block,
      district: location.district,
      state: location.state,
      pincode: location.pincode,
    },
    available_margin: Number(availableMargin),
    language,
  });
  return unwrap(response);
  // -> { market_reach, opportunity_analysis, swot, threats,
  //      competitor_density, pricing_suggestion }
};

// Dynamic AI/user content translation. Static UI strings live in src/locales;
// this endpoint is only for text whose content is not known at build time.
export const translateText = async ({ text, sourceLanguage = "en-IN", targetLanguage }) => {
  const response = await api.post("/api/v1/translate", {
    text,
    source_language: sourceLanguage,
    target_language: targetLanguage,
  });
  return unwrap(response)?.translated_text || text;
};

// -----------------------------------------------------------------------
// Reports — matches server/app/api/v1/routes_reports.py
// Reports are registered under /api/v1/reports on the backend.
// -----------------------------------------------------------------------

export const listReports = async () => {
  const response = await api.get("/api/v1/reports");
  return unwrap(response);
};

export const saveReport = async (payload) => {
  const response = await api.post("/api/v1/reports", payload);
  return unwrap(response);
};

// -----------------------------------------------------------------------
// Auth — matches server/app/api/v1/routes_auth.py
// NOTE: the backend currently only exposes GET /auth/status as a
// health-style stub. There is no real /auth/login or /auth/register
// endpoint yet, and password hashing/JWT issuing on the backend is a
// placeholder (see INTEGRATION_NOTES.md). Login/Register pages use a
// local mock in AuthContext until those endpoints are real — swap the
// mock calls in AuthContext.jsx for these once the backend is ready.
// -----------------------------------------------------------------------

export const getAuthStatus = async () => {
  const response = await api.get("/api/v1/auth/status");
  return unwrap(response);
};

export default api;
