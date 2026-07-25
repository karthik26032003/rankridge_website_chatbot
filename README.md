# Rankridge Website Chatbot

FastAPI backend for **Rankridge Assistant ("Raju")** — the admissions chatbot that
answers IIT-JEE, NEET & EAMCET questions strictly from a curated knowledge file and
captures visitor email leads.

It powers the `ChatWidget` on the [Rankridge website](https://github.com/karthik26032003/rankridge_website),
which calls this backend's `/chat/*` API. A standalone test UI is also bundled in
[`frontend/`](frontend/) and served at `/`.

## Tech

- **FastAPI** + **Uvicorn** (streaming responses)
- **SQLAlchemy** (SQLite by default; Postgres in production)
- **OpenAI** chat completions
- Managed with **[uv](https://docs.astral.sh/uv/)**

## Project structure

```
backend/
  main.py               # app entry, CORS, static test UI, /health
  routers/              # HTTP endpoints
    chat.py             #   /chat/start, /chat/stream, /chat/{id}
    leads.py            #   /leads (admin-key protected)
  models/               # SQLAlchemy models + pydantic schema
    chat_model.py  message_model.py  lead_model.py  message.py
  helpers/
    config.py           # env-driven settings + system-prompt builder
    database.py         # engine / session
    rate_limit.py       # per-IP rate limiting
    services/           # business logic
      chat_service.py  memory_service.py  lead_service.py  openai_service.py
frontend/               # standalone test chat UI (served at /)
website_knowledge.txt   # the ONLY facts the assistant may use — edit anytime
```

## Setup & run (uv)

```bash
# 1. Install dependencies into a managed venv
uv sync

# 2. Configure environment
cp .env.example .env      # then fill in OPENAI_API_KEY and ADMIN_KEY

# 3. Run (dev, auto-reload)
uv run uvicorn backend.main:app --reload
```

- Test UI: <http://127.0.0.1:8000/>
- Health check: <http://127.0.0.1:8000/health>

## Configuration

All settings come from `.env` (see [`.env.example`](.env.example)):

| Variable | Required | Notes |
|---|---|---|
| `OPENAI_API_KEY` | yes | OpenAI key |
| `MODEL_NAME` | yes | e.g. `gpt-4o-mini` |
| `ADMIN_KEY` | yes | protects the `/leads` endpoint |
| `SYSTEM_PROMPT` | recommended | Raju persona; `{{WEBSITE_KNOWLEDGE}}` is injected at runtime |
| `TEMPERATURE`, `MAX_TOKENS` | no | generation tuning |
| `DATABASE_URL` | no | defaults to local SQLite; set a Postgres URL in production |
| `ALLOWED_ORIGINS` | no | comma-separated CORS origins (`*` = any) |

The assistant's knowledge lives in `website_knowledge.txt`. Edits take effect
immediately — no restart needed.

## API

| Method | Path | Purpose |
|---|---|---|
| `POST` | `/chat/start` | Save the user message, create the chat if new |
| `POST` | `/chat/stream` | Stream the assistant reply (`text/plain`) |
| `GET` | `/chat/{chat_id}` | Fetch a chat's message history |
| `GET` | `/leads` | List captured email leads (admin) |
| `GET` | `/health` | Liveness probe |

`/leads` accepts the admin key via the `X-Admin-Key` header (preferred) or a
`?key=` query param.

## Deploying to Railway

1. Push to GitHub and create a Railway project from this repo.
2. Set the environment variables above in Railway → **Variables**.
3. The bundled [`nixpacks.toml`](nixpacks.toml) pins the build: it installs from
   `uv.lock` and starts with
   `uv run uvicorn backend.main:app --host 0.0.0.0 --port $PORT`.
4. **Persistence:** the default SQLite file lives on Railway's ephemeral disk and
   is wiped on every redeploy. Add a Railway **Postgres** database and set
   `DATABASE_URL` to `${{Postgres.DATABASE_URL}}` so captured leads survive. The
   Postgres driver (`psycopg`) is already included.

## Connecting the website

The website's `ChatWidget` uses `API_BASE = '/api'`, which only resolves via the
Next dev-server rewrite. In production (static export), point the widget at this
backend's deployed URL instead (e.g. `https://<app>.up.railway.app`). CORS here
defaults to `*`, so cross-origin calls work; tighten `ALLOWED_ORIGINS` to the
site's domain once the URL is fixed.