import ee
import os
from dotenv import load_dotenv

load_dotenv()

def initialize_gee():
    project_id = os.getenv("GEE_PROJECT_ID")

    print("Loaded project id:", project_id)  # TEMP DEBUG LINE

    if not project_id:
        raise ValueError("GEE_PROJECT_ID not found in .env file.")

    ee.Initialize(project=project_id)
    print("GEE initialized successfully")