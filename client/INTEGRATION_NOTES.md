# Frontend — Integration Notes

This is the corrected `client/` folder for `sih26091-rural-advisor`. The frontend
is fully coded and builds cleanly (`npm run build` verified). What follows is
exactly what the backend needs to provide for every screen to work end-to-end.

## What was fixed here

- **Field-name mismatches** between `api.js` and the backend Pydantic schemas
  (was sending `available_capital`/`business_type`, backend wants
  `available_margin`/`business_category`, and `location` must be
  `{ village, block, district, state }`, not a flat string).
- **Response envelope wasn't being unwrapped.** Backend returns
  `{ success, data, error }`; every `api.js` function now unwraps `.data`
  before returning, so pages/components never guess field names again.
- **`FeasibilityReport.jsx` was reading fields that don't exist** on the real
  backend response. Rewired to the actual shape: `market_reach`,
  `opportunity_analysis`, `swot`, `competitor_density`, `pricing_suggestion`.
- **Unused built components wired in**: `SWOTCard`, `MarketReachMap`,
  `CompetitorChart`, `PricingSuggestion`, `SchemeCard`, `EMITable`,
  `MoratoriumTimeline` are now actually rendered instead of sitting unused.
- **Real routing** via `react-router-dom` (already a dependency, wasn't used)
  replacing the manual `window.location.pathname` check — `Login`, `Register`,
  `Dashboard` are now reachable.
- **EMI schedule endpoint wired in** — `FinancialCalculator` now offers a
  "View detailed repayment schedule" button calling `/emi-schedule`, which
  wasn't called from the frontend at all before.
- **Voice input** uses the browser's native Web Speech API directly (works
  regardless of Bhashini's status) on the feasibility form's village field.

## What the backend still needs to do (blocking, in priority order)

1. **`server/app/main.py` only registers `routes_calculator` (twice) and
   `routes_advisory`.** `routes_auth`, `routes_market`, `routes_reports`,
   `routes_translate` exist as files but return 404 right now. This blocks:
   `Dashboard.jsx` (`GET /api/v1/reports`), `FeasibilityReport.jsx`'s save
   button (`POST /api/v1/reports`), and `Navbar`'s auth check.
2. **No real `/api/v1/auth/login` or `/api/v1/auth/register` endpoints.**
   `Login.jsx` / `Register.jsx` currently call a mock in `AuthContext.jsx`
   (clearly marked with `// TODO`) so the UI and routing can be demoed and
   tested without waiting on this. Swap the mock functions for real
   `api.js` calls once the backend has them — the request/response shape
   the frontend expects is documented right in `AuthContext.jsx`.
3. **`server/app/core/security.py` doesn't actually hash passwords or sign
   tokens** — `hash_password` returns plaintext, `create_access_token` isn't
   a JWT. Not a frontend issue, but real login can't be wired in safely
   until this is fixed, since `passlib` and `python-jose` are already in
   `requirements.txt` and just aren't being used.
4. **Advisory, geo, LLM, translation, and RAG services are all stubs**
   (`bhashini_client.py`, `llm_client.py`, `geo_service.py`, `rag/*`, all four
   `data_pipeline/loaders/*`) — the feasibility report currently always
   returns the same hardcoded dummy data regardless of input. The frontend
   is built against the *shape* of that dummy response, so once real logic
   replaces it, as long as the shape (`market_reach`, `swot`, etc.) stays the
   same, no frontend changes should be needed.

## Exact request contracts the frontend sends

- `POST /api/v1/calculator/calculate-eligibility` → `{ available_margin: number }`
- `POST /api/v1/calculator/emi-schedule` → `{ loan_amount, interest_rate, tenure_years, moratorium_months }`
- `POST /api/v1/advisory/feasibility-report` → `{ business_category, location: { village, block, district, state }, available_margin, language }`
- `GET /api/v1/reports`, `POST /api/v1/reports` — not yet reachable, see #1 above
- `GET /api/v1/auth/status` — reachable today, but there's no login/register endpoint yet

## Running locally

```bash
npm install
npm start        # dev server on :3000, proxies to REACT_APP_API_URL (defaults to :8000)
npm run build     # production build — verified working
```

Set `REACT_APP_API_URL` if the backend isn't on `localhost:8000`.
