# Volleyball Team Matcher

A full-stack volleyball team matching app with a FastAPI backend and a React + Vite frontend.

## Stack

- Backend: FastAPI, SQLAlchemy 2.0, JWT auth
- Frontend: React, Vite, TailwindCSS
- Database: SQLite locally (Postgres recommended for production)

## Repo structure

- `api/` FastAPI app (Vercel Python entrypoint is `api/index.py`)
- `alembic/` migrations
- `frontend/` React SPA
- `tests/` pytest suite
- `vercel.json` Vercel routing and build config

## Environment variables

Set these in your shell or Vercel project settings:

- `DATABASE_URL` (example: `sqlite:///./app.db` or `postgresql+psycopg://user:pass@host/db`)
- `JWT_SECRET` (a long random string)
- `VITE_API_BASE` (frontend only, example: `http://localhost:8000/api`)
- `SEED_USERS` (optional, default `true` to insert the seed list on startup)
- `ALLOW_SELF_REGISTER` (optional, default `false` to block unknown names)
- `MIN_VOTERS_FOR_RESULTS` (optional, default `12`)

## Local setup

Backend:

```bash
python -m venv .venv
. .venv/bin/activate  # on Windows: .venv\Scripts\Activate.ps1
pip install -r requirements.txt
alembic upgrade head
uvicorn api.index:app --reload
```

Frontend:

```bash
cd frontend
npm install
npm run dev
```

If the backend runs on a different port locally, export the API base:

```bash
export VITE_API_BASE=http://localhost:8000/api
npm run dev
```

## Auth flow

There is no separate registration step. Use the login screen with a name only; small typos are matched to the closest name.
The seed list lives in `api/app/seed.py` — edit it to add/remove names.

## Running tests

```bash
pytest
```

## Vercel deployment

1. Push this repository to GitHub.
2. Create a new Vercel project and import the GitHub repo.
3. Ensure the build settings match:
   - Build command: `cd frontend && npm install && npm run build`
   - Output directory: `frontend/dist`
4. Add env vars in Vercel Project Settings:
   - `DATABASE_URL`
   - `JWT_SECRET`

The `vercel.json` routes `/api/*` to the FastAPI app and serves the SPA for other paths.

## Push to GitHub

```bash
git init
git add .
git commit -m "feat: scaffold volleyball matcher app"
git remote add origin <YOUR_GITHUB_REPO_URL>
git push -u origin main
```

## Commit history example

```bash
git commit -m "feat: add FastAPI models, auth, and team logic"
git commit -m "test: cover auth, voting, and team generation"
git commit -m "feat: build React SPA with voting and teams"
git commit -m "chore: add Vercel config and README"
```
