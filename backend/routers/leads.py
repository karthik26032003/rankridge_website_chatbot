import secrets

from fastapi import APIRouter, Header, HTTPException, Query

from backend.helpers.config import settings
from backend.helpers.services.lead_service import get_all_leads

router = APIRouter()


def _authorize(provided_key: str | None) -> None:
    # Constant-time comparison avoids leaking the key through response timing.
    # Accept the key via the X-Admin-Key header (preferred, kept out of access
    # logs) or the legacy ?key= query param.
    if not provided_key or not secrets.compare_digest(provided_key, settings.ADMIN_KEY):
        raise HTTPException(status_code=401, detail="Invalid or missing key.")


@router.get("/leads")
def get_leads_endpoint(
    key: str | None = Query(default=None),
    x_admin_key: str | None = Header(default=None),
):
    _authorize(x_admin_key or key)
    return get_all_leads()
