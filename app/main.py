import truststore
truststore.inject_into_ssl()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from app.api.routes.chat import router as chat_router
from app.api.routes.leads import router as leads_router
from app.db.database import Base, engine
from app.models.chat_model import Chat
from app.models.message_model import MessageDB
from app.models.lead_model import Lead


Base.metadata.create_all(bind=engine)

app = FastAPI(title="Chatbot Backend")


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(chat_router)
app.include_router(leads_router)


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


app.mount("/static", StaticFiles(directory="frontend"), name="static")


@app.get("/")
def serve_frontend():
    return FileResponse("frontend/index.html")