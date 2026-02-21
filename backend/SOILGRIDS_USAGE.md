# SoilGrids Integration - Usage Examples

## Overview
This module integrates SoilGrids v2.0 API to fetch soil properties (pH, clay, sand, silt) and classify soil texture.

## Features
- ✅ No API key required
- ✅ Simple coordinate-based queries (latitude, longitude)
- ✅ Extracts MEAN values for 0-5cm depth
- ✅ Classifies soil texture (clayey, sandy, silty, loamy)
- ✅ Rule-based classification (no ML)
- ✅ FastAPI endpoints included

---

## 1. Standalone Python Usage

### Basic Example

```python
from app.soilgrids_service import fetch_soil_data

# Fetch soil data for coordinates
latitude = 10.8505
longitude = 76.2711

soil_data = fetch_soil_data(latitude, longitude)

print(soil_data)
# Output:
# {
#     'soil_ph': 5.8,
#     'clay': 28.5,
#     'sand': 45.2,
#     'silt': 26.3,
#     'soil_texture': 'loamy'
# }
```

### With Error Handling

```python
from app.soilgrids_service import fetch_soil_data, SoilGridsError

try:
    soil_data = fetch_soil_data(latitude=10.8505, longitude=76.2711)
    
    print(f"pH: {soil_data['soil_ph']}")
    print(f"Texture: {soil_data['soil_texture']}")
    print(f"Clay: {soil_data['clay']}%")
    
except ValueError as e:
    print(f"Invalid coordinates: {e}")
except SoilGridsError as e:
    print(f"API error: {e}")
```

### Get Texture Description

```python
from app.soilgrids_service import fetch_soil_data, get_soil_texture_description

soil_data = fetch_soil_data(10.8505, 76.2711)
description = get_soil_texture_description(soil_data['soil_texture'])

print(description)
# Output: "Balanced mix - ideal for most crops, good water retention and drainage"
```

---

## 2. API Usage

### Start the Server

```bash
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### POST Request

```bash
curl -X POST "http://localhost:8000/api/soil/query" \
  -H "Content-Type: application/json" \
  -d '{
    "latitude": 10.8505,
    "longitude": 76.2711
  }'
```

**Response:**
```json
{
  "soil_ph": 5.8,
  "clay": 28.5,
  "sand": 45.2,
  "silt": 26.3,
  "soil_texture": "loamy",
  "texture_description": "Balanced mix - ideal for most crops, good water retention and drainage"
}
```

### GET Request

```bash
curl "http://localhost:8000/api/soil/query?latitude=10.8505&longitude=76.2711"
```

---

## 3. Integration with Frontend (React)

```javascript
// Fetch soil data from your React app
async function getSoilData(latitude, longitude) {
  const response = await fetch('http://localhost:8000/api/soil/query', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      latitude: latitude,
      longitude: longitude
    })
  });
  
  if (!response.ok) {
    throw new Error('Failed to fetch soil data');
  }
  
  const data = await response.json();
  return data;
}

// Usage
getSoilData(10.8505, 76.2711)
  .then(soilData => {
    console.log('Soil pH:', soilData.soil_ph);
    console.log('Texture:', soilData.soil_texture);
    console.log('Description:', soilData.texture_description);
  })
  .catch(error => console.error('Error:', error));
```

---

## 4. Soil Texture Classification Rules

The module uses simplified USDA classification:

| Texture | Rule | Characteristics |
|---------|------|-----------------|
| **Clayey** | clay ≥ 40% | High water retention, slow drainage |
| **Sandy** | sand ≥ 70% | Fast drainage, low water retention |
| **Silty** | silt ≥ 60% | Smooth texture, moderate retention |
| **Loamy** | Balanced mix | Ideal for crops, good retention & drainage |

---

## 5. Example Test Coordinates

| Location | Latitude | Longitude | Expected Type |
|----------|----------|-----------|---------------|
| Kerala, India | 10.8505 | 76.2711 | Varies |
| Iowa, USA (farm belt) | 42.0 | -93.5 | Loamy |
| Sahara Desert | 25.0 | 15.0 | Sandy |
| Amazon Rainforest | -3.0 | -60.0 | Clayey |

---

## 6. Response Format

```python
{
    'soil_ph': float,           # pH value (e.g., 5.8)
    'clay': float,              # Clay % (0-100)
    'sand': float,              # Sand % (0-100)
    'silt': float,              # Silt % (0-100)
    'soil_texture': str         # 'clayey', 'sandy', 'silty', or 'loamy'
}
```

---

## 7. Error Handling

### Possible Errors

- `ValueError`: Invalid coordinates (out of range)
- `SoilGridsError`: API request failed or invalid response
  - Timeout
  - Connection error
  - HTTP error
  - Invalid JSON

### Example

```python
try:
    soil_data = fetch_soil_data(95, 200)  # Invalid coordinates
except ValueError as e:
    print(e)  # "Latitude must be between -90 and 90, got 95"
```

---

## 8. Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Or install individually
pip install fastapi uvicorn requests pydantic python-dotenv
```

---

## Notes

- **No API key required** - SoilGrids is free and open
- **Depth layer**: Currently uses 0-5cm (can be extended to 0-30cm average)
- **Data source**: ISRIC SoilGrids v2.0 (250m resolution)
- **Coverage**: Global
- **No rate limits** for reasonable usage

---

## API Documentation

Once server is running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
