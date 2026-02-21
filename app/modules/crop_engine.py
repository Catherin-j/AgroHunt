# app/modules/crop_engine.py

import requests
import ee
from app.config import supabase


# =====================================================
# 1️⃣ Fetch Climate Data
# =====================================================

def fetch_climate(lat: float, lon: float, year: int = 2023):

    url = "https://power.larc.nasa.gov/api/temporal/daily/point"

    params = {
        "parameters": "T2M,PRECTOTCORR",
        "community": "AG",
        "longitude": lon,
        "latitude": lat,
        "start": f"{year}0101",
        "end": f"{year}1231",
        "format": "json"
    }

    response = requests.get(url, params=params, timeout=15)
    response.raise_for_status()

    data = response.json()

    temps = list(data["properties"]["parameter"]["T2M"].values())
    rains = list(data["properties"]["parameter"]["PRECTOTCORR"].values())

    mean_temp = sum(temps) / len(temps)
    total_rain = sum(rains)

    return total_rain, mean_temp


# =====================================================
# 2️⃣ Elevation from SRTM
# =====================================================

def get_elevation(polygon_ee):

    srtm = ee.Image("USGS/SRTMGL1_003")

    stats = srtm.reduceRegion(
        reducer=ee.Reducer.mean(),
        geometry=polygon_ee,
        scale=30
    )

    elevation = stats.get("elevation").getInfo()

    return elevation


# =====================================================
# 3️⃣ Crop Requirements
# =====================================================

def get_crop_requirements(crop: str):

    crop = crop.strip().lower()

    print("Looking for crop:", crop)

    # Print all rows
    all_rows = supabase.table("crop_requirements").select("*").execute()
    print("ALL ROWS:", all_rows.data)

    response = (
        supabase.table("crop_requirements")
        .select("*")
        .ilike("crop_name", crop)
        .execute()
    )

    print("MATCH RESULT:", response.data)

    if not response.data:
        raise ValueError(f"Crop '{crop}' not found in database")

    row = response.data[0]

    return {
        "rain": (
            row["rainfall_abs_min"],
            row["rainfall_opt_min"],
            row["rainfall_opt_max"],
            row["rainfall_abs_max"]
        ),
        "temp": (
            row["temp_abs_min"],
            row["temp_opt_min"],
            row["temp_opt_max"],
            row["temp_abs_max"]
        ),
        "elev": (
            row["elev_abs_min"],
            row["elev_opt_min"],
            row["elev_opt_max"],
            row["elev_abs_max"]
        )
    }
# =====================================================
# 4️⃣ Trapezoidal Suitability
# =====================================================

def trapezoidal_suitability(value, abs_min, opt_min, opt_max, abs_max):

    if value <= abs_min or value >= abs_max:
        return 0.0

    if opt_min <= value <= opt_max:
        return 1.0

    if abs_min < value < opt_min:
        return (value - abs_min) / (opt_min - abs_min)

    if opt_max < value < abs_max:
        return (abs_max - value) / (abs_max - opt_max)

    return 0.0


# =====================================================
# 5️⃣ Final Crop Evaluation
# =====================================================

def evaluate_crop(polygon_ee, crop: str, lat: float, lon: float):

    rainfall, temperature = fetch_climate(lat, lon)
    elevation = get_elevation(polygon_ee)

    crop_data = get_crop_requirements(crop)

    rainfall_score = trapezoidal_suitability(rainfall, *crop_data["rain"])
    temp_score = trapezoidal_suitability(temperature, *crop_data["temp"])
    elev_score = trapezoidal_suitability(elevation, *crop_data["elev"])

    if rainfall_score == 0:
        crop_score = 0.0
        climate_flag = "Rainfall unsuitable — crop rejected."
    else:
        crop_score = (
            0.45 * rainfall_score +
            0.45 * temp_score +
            0.10 * elev_score
        )
        climate_flag = "Climate conditions acceptable."

    return {
        "rainfall_mm": rainfall,
        "temperature_c": temperature,
        "elevation_m": elevation,
        "rainfall_score": round(rainfall_score, 3),
        "temperature_score": round(temp_score, 3),
        "elevation_score": round(elev_score, 3),
        "crop_score": round(crop_score, 3),
        "climate_flag": climate_flag
    }