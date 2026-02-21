# app/config.py

import os
import ee
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()

# ===============================
# Earth Engine Initialization
# ===============================

def initialize_gee():
    project_id = os.getenv("GEE_PROJECT_ID")

    if not project_id:
        raise ValueError("GEE_PROJECT_ID not found in .env file.")

    try:
        ee.Initialize(project=project_id)
        print("GEE initialized successfully")
    except Exception:
        ee.Authenticate()
        ee.Initialize(project=project_id)
        print("GEE authenticated and initialized")


# ===============================
# Supabase Initialization
# ===============================

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("Supabase credentials missing in .env file.")

# 🔥 THIS is what crop_engine imports
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
# config.py

# temp validation 
SCORING_WEIGHTS = {
    "geometry": 0.15,
    "ndvi": 0.25,
    "land": 0.25,
    "crop": 0.20,
    "overlap": 0.15
}

PASS_THRESHOLD = 0.65