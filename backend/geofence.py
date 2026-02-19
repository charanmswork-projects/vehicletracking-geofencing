from math import radians, sin, cos, asin, sqrt
from typing import Tuple

# Mean Earth radius in meters (commonly used for haversine)
EARTH_RADIUS_M = 6_371_000.0

def haversine_distance_m(
    lat1: float, lon1: float, lat2: float, lon2: float
) -> float:

    # Convert degrees -> radians
    lat1_r = radians(lat1)
    lon1_r = radians(lon1)
    lat2_r = radians(lat2)
    lon2_r = radians(lon2)

    dlat = lat2_r - lat1_r
    dlon = lon2_r - lon1_r

    a = sin(dlat / 2.0) ** 2 + cos(lat1_r) * cos(lat2_r) * sin(dlon / 2.0) ** 2
    c = 2.0 * asin(sqrt(a))

    return EARTH_RADIUS_M * c


def check_circular_geofence(
    lat: float,
    lon: float,
    center_lat: float,
    center_lon: float,
    radius_m: float,
) -> Tuple[bool, float]:
    """
    Check if (lat, lon) is inside a circular geofence.

    It Returns:
      (inside, distance_m)
    """
    distance_m = haversine_distance_m(lat, lon, center_lat, center_lon)
    inside = distance_m <= radius_m
    return inside, distance_m
