import streamlit as st
from datetime import datetime
from geopy.geocoders import Nominatim
import requests
import pandas as pd

# -----------------------------------
# PAGE CONFIGURATION
# -----------------------------------
st.set_page_config(
    page_title="Taxi Fare Predictor",
    page_icon="🚕",
    layout="centered"
)

# -----------------------------------
# HEADER
# -----------------------------------
st.markdown("""
# 🚕 Taxi Fare Prediction
### Enter your ride details to estimate the taxi fare.
---
""")

# -----------------------------------
# INPUT SECTION
# -----------------------------------
st.header("📝 Ride Information")

col1, col2 = st.columns(2)

with col1:
    date = st.date_input("Pickup date", value=datetime(2025, 11, 15).date())
with col2:
    time = st.time_input("Pickup time", value=datetime(2025, 11, 15, 14, 0).time())

pickup_datetime = datetime.combine(date, time)

passenger_count = st.number_input(
    "Number of passengers:",
    min_value=1,
    max_value=6,
    value=1
)

# -----------------------------------
# ADDRESS INPUTS
# -----------------------------------
st.header("Addresses")

pickup_address = st.text_input(
    "Pickup location:",
    "Empire State Building, New York"
)

dropoff_address = st.text_input(
    "Dropoff location:",
    "Times Square, New York"
)

# Geocoder
geolocator = Nominatim(user_agent="taxifare_app")

def address_to_latlon(address):
    try:
        location = geolocator.geocode(address)
        if location:
            return location.latitude, location.longitude
    except:
        pass
    return None, None

# -----------------------------------
# PREDICTION BUTTON
# -----------------------------------
if st.button("💰 Predict Fare", type="primary"):

    pickup_lat, pickup_lon = address_to_latlon(pickup_address)
    drop_lat, drop_lon = address_to_latlon(dropoff_address)

    if pickup_lat is None:
        st.error("❌ Pickup address not found. Please try a different address.")

    if drop_lat is None:
        st.error("❌ Dropoff address not found. Please try a different address.")

    if pickup_lat and drop_lat:

        # -----------------------------------
        # MAP SECTION
        # -----------------------------------
        st.header("🗺️ Route Map")
        st.markdown(
            "The map below shows both the pickup and dropoff locations. "
            "This helps verify that the geocoding process worked correctly."
        )

        map_df = pd.DataFrame(
            [
                {"lat": pickup_lat, "lon": pickup_lon},
                {"lat": drop_lat, "lon": drop_lon}
            ]
        )

        st.map(map_df, zoom=12)

        st.markdown(
            f"""
            **Map summary:**
            - Pickup: `{pickup_address}`
            - Dropoff: `{dropoff_address}`
            - Distance approximated visually
            """
        )

        # -----------------------------------
        # API CALL
        # -----------------------------------
        url = "https://taxifare.lewagon.ai/predict"

        params = {
            "pickup_datetime": pickup_datetime.isoformat(),
            "pickup_longitude": pickup_lon,
            "pickup_latitude": pickup_lat,
            "dropoff_longitude": drop_lon,
            "dropoff_latitude": drop_lat,
            "passenger_count": passenger_count
        }

        try:
            response = requests.get(url, params=params)
            result = response.json()
            fare = result.get("fare")

            # -----------------------------------
            # PREDICTION RESULT
            # -----------------------------------
            st.header("💵 Estimated Fare")

            if fare:
                st.success(f"Estimated Fare: **${fare:.2f}**")
                st.caption("This is an approximation based on historical NYC taxi data.")
            else:
                st.error("The API did not return a valid fare.")

        except Exception as e:
            st.error(f"API request error: {e}")

# -----------------------------------
# ACCESSIBILITY FOOTER
# -----------------------------------
st.markdown("---")
