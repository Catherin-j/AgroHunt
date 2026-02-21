# AgroHunt Backend

FastAPI backend service for precision agriculture and crop analysis.

## Features

### 🌍 SoilGrids Integration
- Fetch soil properties (pH, clay, sand, silt) using coordinates
- Rule-based soil texture classification
- No API key required
- Global coverage at 250m resolution

### 🚀 API Endpoints
- `POST /api/soil/query` - Get soil data by coordinates
- `GET /api/soil/query` - Alternative GET endpoint
- `GET /health` - Health check

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Run the Server

```bash
# Development mode
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Production mode
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### 3. Test the API

```bash
# Test soil data endpoint
curl -X POST "http://localhost:8000/api/soil/query" \
  -H "Content-Type: application/json" \
  -d '{"latitude": 10.8505, "longitude": 76.2711}'
```

## Testing

Run the test suite:

```bash
cd backend
python test_soilgrids.py
```

## Documentation

- **SoilGrids Usage Guide**: See [SOILGRIDS_USAGE.md](SOILGRIDS_USAGE.md)
- **API Documentation**: http://localhost:8000/docs (Swagger UI)
- **ReDoc**: http://localhost:8000/redoc

## Project Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI application
│   ├── soilgrids_service.py    # SoilGrids API integration
│   └── schemas.py              # Pydantic models (future)
├── test_soilgrids.py           # Test suite
├── requirements.txt            # Python dependencies
├── README.md                   # This file
└── SOILGRIDS_USAGE.md         # Detailed usage guide
```

## API Usage Examples

### Python

```python
import requests

response = requests.post('http://localhost:8000/api/soil/query', json={
    'latitude': 10.8505,
    'longitude': 76.2711
})

soil_data = response.json()
print(f"Soil pH: {soil_data['soil_ph']}")
print(f"Texture: {soil_data['soil_texture']}")
```

### JavaScript/React

```javascript
const getSoilData = async (lat, lon) => {
  const response = await fetch('http://localhost:8000/api/soil/query', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ latitude: lat, longitude: lon })
  });
  return await response.json();
};
```

### cURL

```bash
curl "http://localhost:8000/api/soil/query?latitude=10.8505&longitude=76.2711"
```

## Dependencies

- **FastAPI**: Modern web framework
- **Pydantic**: Data validation
- **Requests**: HTTP client for SoilGrids API
- **Uvicorn**: ASGI server

## Environment

Create a `.env` file for configuration (optional):

```env
API_HOST=0.0.0.0
API_PORT=8000
LOG_LEVEL=INFO
```

## Development

### Add New Endpoints

Edit `app/main.py`:

```python
@app.get("/api/new-endpoint")
async def new_endpoint():
    return {"message": "Hello"}
```

### Add New Services

Create new service files in `app/` directory following the pattern of `soilgrids_service.py`.

## License

MIT
