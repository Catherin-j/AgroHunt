# app/config.py

import os
import json
import ee
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()

# =========================================================
# 🌍 EARTH ENGINE INITIALIZATION (STRICT PRODUCTION MODE)
# =========================================================

def initialize_gee():
    """
    Initializes Google Earth Engine using Service Account ONLY.
    No local fallback allowed on server.
    """

    service_account_json = os.getenv("GEE_SERVICE_ACCOUNT_JSON")

    if not service_account_json:
        raise RuntimeError(
            "GEE_SERVICE_ACCOUNT_JSON not found in environment variables."
        )

    try:
        service_account_info = json.loads(service_account_json)

        credentials = ee.ServiceAccountCredentials(
            service_account_info["client_email"],
            key_data=json.dumps(service_account_info)
        )

        ee.Initialize(credentials)
        print("✅ GEE initialized using Service Account")

    except Exception as e:
        raise RuntimeError(f"❌ GEE initialization failed: {e}")


# =========================================================
# 🗄 SUPABASE INITIALIZATION (Lazy)
# =========================================================

_supabase_client: Client = None


def get_supabase() -> Client:
    """
    Returns the Supabase client, initializing it on first call.
    """
    global _supabase_client

    if _supabase_client is None:
        url = os.getenv("SUPABASE_URL")
        key = os.getenv("SUPABASE_KEY")

        if not url or not key:
            raise ValueError("Supabase credentials missing in environment variables.")

        _supabase_client = create_client(url, key)

    return _supabase_client


def __getattr__(name):
    if name == "supabase":
        return get_supabase()
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


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