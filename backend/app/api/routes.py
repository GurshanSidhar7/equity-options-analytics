"""HTTP routes only. Day 1 exposes application liveness, not market-feed health."""

from fastapi import APIRouter

router = APIRouter()


@router.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
