# app/config.py

import os
import json
import ee
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()

# =========================================================
# 🌍 EARTH ENGINE INITIALIZATION (PRODUCTION SAFE)
# =========================================================

def initialize_gee():
    """
    Initializes Google Earth Engine.

    - On Render → uses Service Account JSON
    - On Local Machine → uses normal project auth
    """

    service_account_json = os.getenv("GEE_SERVICE_ACCOUNT_JSON")
    project_id = os.getenv("GEE_PROJECT_ID")

    if service_account_json:
        # ✅ PRODUCTION MODE (Render)
        try:
            service_account_info = json.loads(service_account_json)

            credentials = ee.ServiceAccountCredentials(
                service_account_info["client_email"],
                key_data=json.dumps(service_account_info)
            )

            ee.Initialize(credentials)
            print("GEE initialized using Service Account")

        except Exception as e:
            raise RuntimeError(f"GEE Service Account init failed: {e}")

    else:
        # ✅ LOCAL DEVELOPMENT MODE
        if not project_id:
            raise ValueError("GEE_PROJECT_ID missing in .env")

        try:
            ee.Initialize(project=project_id)
            print("GEE initialized locally")

        except Exception:
            print("Authenticating GEE locally...")
            ee.Authenticate()
            ee.Initialize(project=project_id)
            print("GEE authenticated and initialized")


# =========================================================
# 🗄 SUPABASE INITIALIZATION
# =========================================================

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("Supabase credentials missing in environment variables.")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)


# =========================================================
# ⚖️ SCORING CONFIGURATION
# =========================================================

SCORING_WEIGHTS = {
    "geometry": 0.15,
    "ndvi": 0.25,
    "land": 0.25,
    "crop": 0.20,
    "overlap": 0.15
}

PASS_THRESHOLD = 0.65