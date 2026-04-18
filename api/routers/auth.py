from fastapi import APIRouter, HTTPException

router = APIRouter()


@router.post("/guest")
async def create_guest_session() -> dict[str, str]:
    """Issue a guest session (no registration)."""
    # TODO: generate UUID, store in Redis with TTL
    return {"session_id": "TODO", "expires_in": "86400"}


@router.post("/email/login")
async def email_login(email: str, password: str) -> dict[str, str]:
    """Email + password login."""
    # TODO: verify against users table, issue JWT
    raise HTTPException(status_code=501, detail="Not implemented in starter")
