# SIH Rural Advisor

A rural business feasibility and finance advisory application with a React client, FastAPI server, and PostgreSQL database.

## Repository Structure

- `client/` React PWA frontend
- `server/` FastAPI backend, business services, data pipeline, and tests
- `docs/` API contracts, data source notes, and architecture diagram

## Run With Docker

```bash
docker compose up --build
```

The client is available at `http://localhost:3000` and the API is available at `http://localhost:8000`.

## Local Development

Install frontend dependencies from `client/` and Python dependencies from `server/requirements.txt`. Copy the environment values in each `.env` file and start PostgreSQL before running the API.
