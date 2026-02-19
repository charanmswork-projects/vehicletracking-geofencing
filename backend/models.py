from datetime import datetime, timezone
from typing import Literal, Optional

from pydantic import BaseModel, Field

class LocationIn(BaseModel):
    """
    This is payload sent from the phone -> backend.
    """
    lat: float = Field(..., ge=-90.0, le=90.0, description="Latitude in degrees")
    lon: float = Field(..., ge=-180.0, le=180.0, description="Longitude in degrees")

    ts: Optional[datetime] = Field(
        default=None,
        description="Timestamp (ISO 8601). If omitted, backend will set it.",
    )


class VehicleStateOut(BaseModel):
    """
    Payload sent from backend -> dashboard.
    """
    lat: Optional[float] = None
    lon: Optional[float] = None
    ts: Optional[datetime] = None

    inside: bool = False
    distance_m: Optional[float] = None

    # this event is useful for alerts ("enter"/"exit")
    event: Literal["none", "enter", "exit"] = "none"

    # This can be optional
    last_update_age_s: Optional[float] = None


def ensure_utc(dt: datetime) -> datetime:
    """
    Utility: ensure timestamps are timezone-aware UTC.
    """
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)
