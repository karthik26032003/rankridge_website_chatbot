from fastapi import APIRouter, HTTPException, Query
from app.core.config import settings
from app.services.lead_service import get_all_leads

router = APIRouter()


@router.get("/leads")
def get_leads_endpoint(key: str = Query(None)):
    if not key or key != settings.ADMIN_KEY:
        raise HTTPException(status_code=401, detail="Invalid or missing key.")

    return get_all_leads()
