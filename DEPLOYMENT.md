# Deployment

This repository contains a Next.js frontend and a FastAPI/PostgreSQL backend. Vercel can deploy the frontend and API as a multi-service project; PostgreSQL still needs a managed provider with persistent storage.

## Deploy the frontend to Vercel

1. Import `MaarifSariyev/AutoBoya` in Vercel.
2. Keep the repository root selected. `vercel.json` defines `frontend` and `backend` services and routes `/api/*` requests to FastAPI.
3. Provision a managed PostgreSQL database and add `DATABASE_URL`, `SECRET_KEY`, `ADMIN_EMAIL`, `ADMIN_PASSWORD`, `ENVIRONMENT=production`, and `CORS_ORIGINS` to the Vercel project environment. Use a unique secret key (at least 32 characters) and unique admin password (at least 12 characters).
4. Deploy. The frontend uses same-origin `/api` requests, so it does not need a separate `NEXT_PUBLIC_API_URL` in Vercel.

## Deploy the backend

For a non-Vercel backend host, deploy the `backend` directory using its Dockerfile and configure these environment variables:

- `DATABASE_URL`: the provider's PostgreSQL connection URL
- `SECRET_KEY`: a fresh, random secret of at least 32 characters
- `ADMIN_EMAIL` and `ADMIN_PASSWORD`: production admin credentials
- `ENVIRONMENT=production`
- `CORS_ORIGINS`: the Vercel production URL, plus any preview/custom domains that need browser access, comma-separated

Run the Alembic migrations with `alembic upgrade head` before starting the API. To populate an empty database with the bundled sample data, run `python database/seeds/seed_data.py` with the backend environment configured. Do not commit `.env` files or production credentials.

## Local Docker setup

Copy `.env.example` to `.env`, change the development admin credentials, and start the services with `docker compose up --build`. If local port `5432` is already occupied, set `POSTGRES_PORT` in `.env` to an available host port, such as `55432`.
