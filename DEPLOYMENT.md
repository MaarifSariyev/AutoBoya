# Deployment

This repository contains a Next.js frontend and a FastAPI/PostgreSQL backend. Vercel hosts the frontend; deploy the API and PostgreSQL to a separate service that supports persistent databases and Python containers.

## Deploy the frontend to Vercel

1. Import `MaarifSariyev/AutoBoya` in Vercel.
2. Set the project Root Directory to `frontend` and keep the Next.js framework preset.
3. Add `NEXT_PUBLIC_API_URL` as an environment variable for Production, Preview, and Development. Set it to the public backend origin, for example `https://api.example.com`, without a trailing slash.
4. Deploy.

## Deploy the backend

Deploy the `backend` directory using its Dockerfile, and provision a PostgreSQL database with persistent storage. Configure these backend environment variables in the hosting provider:

- `DATABASE_URL`: the provider's PostgreSQL connection URL
- `SECRET_KEY`: a fresh, random secret of at least 32 characters
- `ADMIN_EMAIL` and `ADMIN_PASSWORD`: production admin credentials
- `ENVIRONMENT=production`
- `CORS_ORIGINS`: the Vercel production URL, plus any preview/custom domains that need browser access, comma-separated

Run the Alembic migrations with `alembic upgrade head` before starting the API. To populate an empty database with the bundled sample data, run `python database/seeds/seed_data.py` with the backend environment configured. Do not commit `.env` files or production credentials.

## Local Docker setup

Copy `.env.example` to `.env`, change the development admin credentials, and start the services with `docker compose up --build`. If local port `5432` is already occupied, set `POSTGRES_PORT` in `.env` to an available host port, such as `55432`.
