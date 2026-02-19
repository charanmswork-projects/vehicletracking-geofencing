"""
In-memory state manager for:
- latest GPS location
- geofence inside/outside status
- enter/exit event detection
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from threading import Lock
from typing import Optional, Literal

from .config import GEOFENCE
from .geofence import check_circular_geofence
from .models import LocationIn, VehicleStateOut, ensure_utc


EventType = Literal["none", "enter", "exit"]


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


@dataclass
class _VehicleState:
    lat: Optional[float] = None
    lon: Optional[float] = None
    ts: Optional[datetime] = None

    inside: bool = False
    distance_m: Optional[float] = None

    event: EventType = "none"


class VehicleStateStore:

    def __init__(self) -> None:
        self._lock = Lock()
        self._state = _VehicleState()
        self._prev_inside: Optional[bool] = None  # for enter/exit detection

    def update_from_location(self, loc: LocationIn) -> VehicleStateOut:
        
        with self._lock:
            ts = loc.ts if loc.ts is not None else _utcnow()
            ts = ensure_utc(ts)

            inside, distance_m = check_circular_geofence(
                lat=loc.lat,
                lon=loc.lon,
                center_lat=GEOFENCE.center_lat,
                center_lon=GEOFENCE.center_lon,
                radius_m=GEOFENCE.radius_m,
            )

            event: EventType = "none"
            if self._prev_inside is not None:
                if (self._prev_inside is False) and (inside is True):
                    event = "enter"
                elif (self._prev_inside is True) and (inside is False):
                    event = "exit"

            self._state.lat = loc.lat
            self._state.lon = loc.lon
            self._state.ts = ts
            self._state.inside = inside
            self._state.distance_m = float(distance_m)
            self._state.event = event

            self._prev_inside = inside

            return self._to_out_locked()

    def get_state(self) -> VehicleStateOut:
    
        with self._lock:
            return self._to_out_locked()

    def _to_out_locked(self) -> VehicleStateOut:
        
        age_s: Optional[float] = None
        if self._state.ts is not None:
            age_s = (_utcnow() - self._state.ts).total_seconds()

        return VehicleStateOut(
            lat=self._state.lat,
            lon=self._state.lon,
            ts=self._state.ts,
            inside=self._state.inside,
            distance_m=self._state.distance_m,
            event=self._state.event,
            last_update_age_s=age_s,
        )


vehicle_store = VehicleStateStore()
    