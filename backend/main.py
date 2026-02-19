"""
FastAPI app entrypoint.
Endpoints:
- POST /location  (phone -> backend)
- GET  /state     (dashboard -> backend)
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import APP, GEOFENCE
from .models import LocationIn, VehicleStateOut
from .state import vehicle_store

app = FastAPI(
    title="Mini Telematics Backend (AVL + Geofence)",
    version="0.1.0",
)


# --- CORS ---
if APP.allow_all_cors:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=False,
        allow_methods=["*"],
        allow_headers=["*"],
    )


@app.get("/health")
def health():
    return {
        "status": "ok",
        "geofence": {
            "center_lat": GEOFENCE.center_lat,
            "center_lon": GEOFENCE.center_lon,
            "radius_m": GEOFENCE.radius_m,
        },
    }


@app.post("/location", response_model=VehicleStateOut)
def post_location(loc: LocationIn) -> VehicleStateOut:

    return vehicle_store.update_from_location(loc)


@app.get("/state", response_model=VehicleStateOut)
def get_state() -> VehicleStateOut:
    
    return vehicle_store.get_state()
