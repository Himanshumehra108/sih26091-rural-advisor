# API Contracts

The client communicates with the FastAPI service under `/api/v1`.

## Health

`GET /health`

```json
{"status":"ok"}
```

## Eligibility

`POST /api/v1/calculator/calculate-eligibility`

```json
{"available_capital": 140000}
```

## Feasibility Report

`POST /api/v1/advisory/feasibility-report`

```json
{
  "business_type": "Dairy",
  "location": "Nashik",
  "available_capital": 140000
}
```
