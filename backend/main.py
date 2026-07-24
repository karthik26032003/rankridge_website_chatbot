import truststore
truststore.inject_into_ssl()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from backend.helpers.config import settings, BASE_DIR
from backend.helpers.database import Base, engine
from backend.routers.chat import router as chat_router
from backend.routers.leads import router as leads_router

# Import the models so their tables register on Base before create_all runs.
from backend.models.chat_model import Chat  # noqa: F401
from backend.models.message_model import MessageDB  # noqa: F401
from backend.models.lead_model import Lead  # noqa: F401

FRONTEND_DIR = BASE_DIR / "frontend"

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Rankridge Chatbot Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins_list,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat_router)
app.include_router(leads_router)


@app.get("/health")
def health_check():
    return {"status": "ok"}


# During active development, stop the browser from caching CSS/JS so UI edits
# always show up on refresh (no more stale-cache confusion).
@app.middleware("http")
async def no_cache_static(request, call_next):
    response = await call_next(request)
    if request.url.path.startswith("/static"):
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
    return response


# The standalone test UI in ./frontend is served at / as a dev/test harness.
# The production client is the website's own ChatWidget, which calls the same
# /chat/* API cross-origin (allowed by CORS above).
app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")


@app.get("/")
def serve_frontend():
    return FileResponse(FRONTEND_DIR / "index.html")
