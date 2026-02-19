from dataclasses import dataclass

@dataclass(frozen=True)
class GeofenceConfig:
    center_lat: float = 50.822949   # Lat and lon can be changed according to requirements
    center_lon: float = 12.930395
    radius_m: float = 50.0         # Geofence radius in meters
50.819261, 12.935137

@dataclass(frozen=True)
class AppConfig:
    expected_update_period_s: float = 2.0
    allow_all_cors: bool = True

GEOFENCE = GeofenceConfig()
APP = AppConfig()
