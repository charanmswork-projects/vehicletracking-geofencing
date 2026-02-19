import time
import requests
import streamlit as st
import folium
from streamlit_folium import st_folium

# Using LOCAL backend (same WiFi):

BACKEND_BASE = "http://127.0.0.1:8000"  

STATE_URL = f"{BACKEND_BASE}/state"
HEALTH_URL = f"{BACKEND_BASE}/health"

st.set_page_config(page_title="Fleet Dashboard - AVL + Geofence", layout="wide")

st.title("Fleet Dashboard — Real-Time Tracking + Geofence")

st.sidebar.header("⚙️ Controls")
refresh_s = st.sidebar.slider("Refresh interval (seconds)", 0.5, 5.0, 1.0, 0.5)
auto_refresh = st.sidebar.toggle("Auto-refresh", value=True)

@st.cache_data(ttl=60)
def fetch_geofence():
    r = requests.get(HEALTH_URL, timeout=5)
    r.raise_for_status()
    data = r.json()
    gf = data["geofence"]
    return gf["center_lat"], gf["center_lon"], gf["radius_m"]

def fetch_state():
    r = requests.get(STATE_URL, timeout=5)
    r.raise_for_status()
    return r.json()


def show_banner(state: dict):
    inside = state.get("inside", False)
    event = state.get("event", "none")
    dist = state.get("distance_m", None)

    if inside:
        st.success(f"🟢 Vehicle is INSIDE geofence. Distance to center: {dist:.1f} m" if dist is not None else "🟢 Vehicle is INSIDE geofence.")
    else:
        st.error(f"🔴 Vehicle is OUTSIDE geofence. Distance to center: {dist:.1f} m" if dist is not None else "🔴 Vehicle is OUTSIDE geofence.")

    if event == "enter":
        st.toast("✅ ENTER event detected!", icon="🟢")
        st.info("🟢 Event: ENTER (vehicle just entered the geofence)")
    elif event == "exit":
        st.toast("⚠️ EXIT event detected!", icon="🔴")
        st.warning("🔴 Event: EXIT (vehicle just left the geofence)")

try:
    center_lat, center_lon, radius_m = fetch_geofence()
except Exception as e:
    st.error(f"Cannot reach backend health endpoint: {e}")
    st.stop()

col1, col2 = st.columns([2, 1], gap="large")

with col2:
    st.subheader("📡 Live Telemetry")
    st.caption(f"Backend: {BACKEND_BASE}")

    try:
        state = fetch_state()
    except Exception as e:
        st.error(f"Cannot fetch state: {e}")
        st.stop()

    st.write("**Lat:**", state.get("lat"))
    st.write("**Lon:**", state.get("lon"))
    st.write("**Timestamp:**", state.get("ts"))
    st.write("**Inside:**", state.get("inside"))
    st.write("**Distance (m):**", state.get("distance_m"))
    st.write("**Event:**", state.get("event"))
    st.write("**Last update age (s):**", state.get("last_update_age_s"))

with col1:
    st.subheader("🗺️ Map View")
    show_banner(state)

    lat = state.get("lat")
    lon = state.get("lon")

    if lat is None or lon is None:
        lat, lon = center_lat, center_lon
        st.info("Waiting for first GPS update… (showing geofence center for now)")

    m = folium.Map(location=[lat, lon], zoom_start=18)

    folium.Circle(
        location=[center_lat, center_lon],
        radius=float(radius_m),
        fill=True,
        fill_opacity=0.08,
        popup=f"Geofence radius: {radius_m} m",
    ).add_to(m)

    folium.Marker(
        location=[lat, lon],
        popup="Vehicle (phone)",
        tooltip="Vehicle position",
        icon=folium.Icon(icon="car", prefix="fa"),
    ).add_to(m)

    st_folium(m, height=520, width=None)

if auto_refresh:
    time.sleep(refresh_s)
    st.rerun()
