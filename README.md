# Agri Plot Validation System

Built for **Problem Statement 3**.

The system checks whether a submitted polygon is a real and plausible agricultural plot, evaluates whether the claimed crop fits location conditions, and returns an explainable decision for audits/disputes.

## What this solves

- Reduces fraud, duplicate claims, and invalid plot submissions.
- Verifies if submitted geometry is likely a real agricultural parcel.
- Validates crop plausibility using climate + elevation + land evidence.
- Produces explainable PASS/REVIEW/FAIL outcomes with module-level evidence.

## System architecture (high level)

Frontend (`React + Leaflet`)  
→ sends plot + crop + farmer id to backend (`FastAPI`)  
→ backend runs modular validation pipeline (`Geometry`, `NDVI`, `Land Use`, `Crop`, `Overlap`)  
→ weighted scoring engine computes final confidence  
→ explainability layer returns human-readable evidence.

### Main components

- `frontend/`: map UI, drawing tools, crop selection, validation trigger.
- `app/main.py`: API entrypoint and orchestration pipeline.
- `app/modules/geometry.py`: geometric plausibility checks and land presence.
- `app/modules/ndvi.py`: vegetation signal from Sentinel-2 NDVI.
- `app/modules/landuse.py`: cropland dominance via Dynamic World yearly mode.
- `app/modules/crop_engine.py`: crop suitability from rainfall, temperature, elevation.
- `app/modules/overlap.py`: duplicate/overlap fraud checks using Supabase PostGIS RPC.
- `app/modules/scoring_engine.py`: MCDA weighted linear combination.
- `app/modules/explainability.py`: auditable explanation + contribution breakdown.

## Validation pipeline details

`POST /validate-plot` runs the following stages:

1. **Geometry validation**
	- Parses GeoJSON polygon and checks self-intersections.
	- Confirms polygon intersects recognized global land boundaries.
	- Computes area (ha), compactness, country/continent context.
	- Applies progressive penalties for very large or irregular parcels.

2. **NDVI vegetation check (Sentinel-2)**
	- Computes yearly mean NDVI and vegetation ratio.
	- Produces `agriculture_score` from NDVI + vegetation ratio.
	- **Hard reject rule:** if `agriculture_score < 0.15` → `FAIL`.

3. **Land-use classification (Dynamic World)**
	- Uses previous complete year and majority class mode.
	- Computes cropland ratio and `land_score` (0–1 continuous score).
	- Handles low-pixel/small polygon reliability issues safely.

4. **Crop plausibility engine**
	- Inputs: claimed crop + polygon centroid.
	- Pulls climate (NASA POWER), elevation (SRTM), crop requirements (Supabase table).
	- Uses trapezoidal suitability for rainfall/temp/elevation and aggregates to `crop_score`.

5. **Overlap/fraud detection**
	- Calls Supabase RPC (`check_overlap`) to compare against existing claims.
	- Returns overlap ratio, overlap score, severity.
	- **Hard reject rule:** severity `critical` → `FAIL`.

6. **Decision aggregation (MCDA)**
	- Weighted final score:
	  - geometry `0.15`
	  - ndvi `0.25`
	  - land `0.25`
	  - crop `0.20`
	  - overlap `0.15`
	- Decision bands:
	  - `PASS` if score `>= 0.65`
	  - `REVIEW` if `0.45 <= score < 0.65`
	  - `FAIL` if score `< 0.45`

7. **Explainability output**
	- Returns final confidence, module contribution breakdown, and plain-language reasons.

## API contract

### Request

`POST /validate-plot`

```json
{
  "farmer_id": "farmer-001",
  "crop": "rice",
  "polygon": {
	 "type": "Polygon",
	 "coordinates": [[[77.1, 28.5], [77.2, 28.5], [77.2, 28.6], [77.1, 28.6], [77.1, 28.5]]]
  }
}
```

### Response (shape)

```json
{
  "decision": "PASS|REVIEW|FAIL",
  "final_score": 0.0,
  "geometry": {},
  "ndvi": {},
  "land_use": {},
  "crop_engine": {},
  "overlap": {},
  "explainability": {
	 "plot_exists": true,
	 "is_agricultural_land": true,
	 "crop_plausible": true,
	 "confidence_score": 0.0,
	 "decision": "PASS|REVIEW|FAIL",
	 "explanation": [],
	 "contribution_breakdown": {}
  }
}
```

## Setup

## 1) Backend

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

Create `.env` in project root:

```env
GEE_PROJECT_ID=your_gee_project
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_key
```

Run backend:

```bash
uvicorn app.main:app --reload --port 8000
```

## 2) Frontend

```bash
cd frontend
npm install
npm run dev
```

Frontend runs on `http://localhost:3000` and proxies `/api/*` to backend (`http://localhost:8000` by default).

## Deliverables mapping (Problem Statement 3)

- **Plot validation score:** `final_score` + module scores.
- **Existence check:** geometry + land intersection validation.
- **Agricultural land check:** NDVI + Dynamic World land-use evidence.
- **Crop plausibility:** climate/elevation/crop requirement suitability.
- **Evidence layers:** Sentinel-2 NDVI, Dynamic World labels, overlap statistics.
- **Clear decision logic:** hard reject rules + confidence bands.
- **API-ready service:** FastAPI endpoint `/validate-plot`.
- **Explainability:** plain-language rationale + contribution breakdown.

## Notes

- `soil.py` exists for SoilGrids integration but is not yet part of the current scoring pipeline.
- Overlap validation depends on a Supabase/PostGIS RPC function named `check_overlap`.
