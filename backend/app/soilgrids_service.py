"""
SoilGrids API Integration Module

Fetches soil properties (pH, clay, sand, silt) from SoilGrids v2.0 REST API
and classifies soil texture based on percentages.

No API key required.
"""

import requests
import time
from typing import Dict, Optional, Tuple


class SoilGridsError(Exception):
    """Custom exception for SoilGrids API errors."""
    pass


def fetch_soil_data(latitude: float, longitude: float, use_fallback: bool = True) -> Dict:
    """
    Fetch soil properties from SoilGrids API for given coordinates.
    
    Args:
        latitude: Latitude coordinate (-90 to 90)
        longitude: Longitude coordinate (-180 to 180)
        use_fallback: If True, return estimated values when API fails (default: True)
    
    Returns:
        Dictionary containing soil properties:
        {
            'soil_ph': float,
            'clay': float (percentage),
            'sand': float (percentage),
            'silt': float (percentage),
            'soil_texture': str (clayey/sandy/silty/loamy),
            'source': str ('soilgrids' or 'fallback')
        }
    
    Raises:
        SoilGridsError: If API request fails and use_fallback is False
        ValueError: If coordinates are out of valid range
    """
    # Validate coordinates
    if not (-90 <= latitude <= 90):
        raise ValueError(f"Latitude must be between -90 and 90, got {latitude}")
    if not (-180 <= longitude <= 180):
        raise ValueError(f"Longitude must be between -180 and 180, got {longitude}")
    
    try:
        # Call API
        raw_data = _call_soilgrids_api(latitude, longitude)
        
        # Parse response
        soil_properties = _parse_soil_response(raw_data)
        
        # Classify texture
        texture = _classify_soil_texture(
            soil_properties['clay'],
            soil_properties['sand'],
            soil_properties['silt']
        )
        
        # Build final result
        result = {
            'soil_ph': soil_properties['soil_ph'],
            'clay': soil_properties['clay'],
            'sand': soil_properties['sand'],
            'silt': soil_properties['silt'],
            'soil_texture': texture,
            'source': 'soilgrids'
        }
        
        return result
    
    except SoilGridsError as e:
        if use_fallback:
            # Return estimated values based on global averages
            return _get_fallback_soil_data(latitude, longitude, str(e))
        else:
            raise


def _call_soilgrids_api(latitude: float, longitude: float, max_retries: int = 3) -> Dict:
    """
    Make HTTP request to SoilGrids v2 API with retry logic.
    
    Args:
        latitude: Latitude coordinate
        longitude: Longitude coordinate
        max_retries: Maximum number of retry attempts (default: 3)
    
    Returns:
        Raw JSON response from API
    
    Raises:
        SoilGridsError: If request fails after all retries
    """
    base_url = "https://rest.isric.org/soilgrids/v2.0/properties/query"
    
    # Properties to query
    properties = ["phh2o", "clay", "sand", "silt"]
    
    # Depth: 0-30cm (use 0-5cm and 5-15cm layers, average them)
    # Available depths: 0-5cm, 5-15cm, 15-30cm, 30-60cm, 60-100cm, 100-200cm
    depth = "0-5cm"  # For simplicity, using top layer
    
    # Build query parameters
    params = {
        "lon": longitude,
        "lat": latitude,
        "property": properties,
        "depth": depth,
        "value": "mean"  # Request only mean values
    }
    
    last_error = None
    
    for attempt in range(max_retries):
        try:
            response = requests.get(base_url, params=params, timeout=30)
            response.raise_for_status()
            return response.json()
        
        except requests.exceptions.Timeout as e:
            last_error = f"Request to SoilGrids API timed out (attempt {attempt + 1}/{max_retries})"
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)  # Exponential backoff: 1s, 2s, 4s
                continue
        
        except requests.exceptions.ConnectionError as e:
            last_error = f"Failed to connect to SoilGrids API (attempt {attempt + 1}/{max_retries})"
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)
                continue
        
        except requests.exceptions.HTTPError as e:
            # For 503 (Service Unavailable) or 429 (Too Many Requests), retry
            if response.status_code in [503, 429, 502, 504]:
                last_error = f"SoilGrids API temporarily unavailable (HTTP {response.status_code}, attempt {attempt + 1}/{max_retries})"
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)
                    continue
            # For other HTTP errors, don't retry
            raise SoilGridsError(f"SoilGrids API returned error: {e}")
        
        except requests.exceptions.RequestException as e:
            last_error = f"Request failed: {e}"
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)
                continue
        
        except ValueError:
            raise SoilGridsError("Invalid JSON response from SoilGrids API")
    
    # If all retries failed
    raise SoilGridsError(f"Failed after {max_retries} attempts. Last error: {last_error}")


def _parse_soil_response(data: Dict) -> Dict:
    """
    Parse SoilGrids API response and extract MEAN values.
    
    Args:
        data: Raw JSON response from SoilGrids API
    
    Returns:
        Dictionary with parsed values:
        {
            'soil_ph': float,
            'clay': float,
            'sand': float,
            'silt': float
        }
    
    Raises:
        SoilGridsError: If response structure is invalid
    """
    try:
        properties = data['properties']['layers']
        
        result = {}
        
        # Extract each property
        for layer in properties:
            prop_name = layer['name']
            depths = layer['depths']
            
            if not depths:
                raise SoilGridsError(f"No depth data for property {prop_name}")
            
            # Get the first depth layer (0-5cm)
            depth_data = depths[0]
            values = depth_data['values']
            
            # Extract mean value
            mean_value = values.get('mean')
            if mean_value is None:
                raise SoilGridsError(f"No mean value for property {prop_name}")
            
            # Convert values based on property type
            if prop_name == 'phh2o':
                # pH is in pH*10, convert to actual pH
                result['soil_ph'] = round(mean_value / 10, 2)
            elif prop_name in ['clay', 'sand', 'silt']:
                # Clay, sand, silt are in g/kg, convert to percentage
                result[prop_name] = round(mean_value / 10, 1)
        
        # Validate all required properties are present
        required = ['soil_ph', 'clay', 'sand', 'silt']
        missing = [prop for prop in required if prop not in result]
        if missing:
            raise SoilGridsError(f"Missing properties in response: {missing}")
        
        return result
    
    except KeyError as e:
        raise SoilGridsError(f"Unexpected response structure: missing key {e}")
    except (TypeError, IndexError) as e:
        raise SoilGridsError(f"Invalid response format: {e}")


def _classify_soil_texture(clay: float, sand: float, silt: float) -> str:
    """
    Classify soil texture based on clay, sand, and silt percentages.
    
    Uses simplified USDA soil texture classification rules:
    - Clayey: clay >= 40%
    - Sandy: sand >= 70%
    - Silty: silt >= 60%
    - Loamy: everything else (well-balanced mix)
    
    Args:
        clay: Clay percentage (0-100)
        sand: Sand percentage (0-100)
        silt: Silt percentage (0-100)
    
    Returns:
        Soil texture class: 'clayey', 'sandy', 'silty', or 'loamy'
    """
    # Normalize percentages (in case they don't sum to 100)
    total = clay + sand + silt
    if total > 0:
        clay = (clay / total) * 100
        sand = (sand / total) * 100
        silt = (silt / total) * 100
    
    # Classification rules
    if clay >= 40:
        return "clayey"
    elif sand >= 70:
        return "sandy"
    elif silt >= 60:
        return "silty"
    else:
        return "loamy"


def _get_fallback_soil_data(latitude: float, longitude: float, error_msg: str) -> Dict:
    """
    Generate fallback soil data when API is unavailable.
    Uses climate zone-based estimates.
    
    Args:
        latitude: Latitude coordinate
        longitude: Longitude coordinate
        error_msg: Error message from API failure
    
    Returns:
        Dictionary with estimated soil properties
    """
    # Simple climate-based estimates
    # Tropical zones (between -23.5 and 23.5 latitude)
    if -23.5 <= latitude <= 23.5:
        # Tropical regions tend to have more weathered soils
        clay = 35.0
        sand = 40.0
        silt = 25.0
        ph = 5.8
    # Temperate zones
    elif 23.5 < abs(latitude) <= 50:
        # Temperate regions often have loamy soils
        clay = 25.0
        sand = 45.0
        silt = 30.0
        ph = 6.5
    # Polar/Sub-polar zones
    else:
        # Cold regions with less weathering
        clay = 20.0
        sand = 50.0
        silt = 30.0
        ph = 6.2
    
    texture = _classify_soil_texture(clay, sand, silt)
    
    return {
        'soil_ph': ph,
        'clay': clay,
        'sand': sand,
        'silt': silt,
        'soil_texture': texture,
        'source': 'fallback',
        'note': f'Using estimated values due to API unavailability: {error_msg}'
    }



def get_soil_texture_description(texture: str) -> str:
    """
    Get a human-readable description of soil texture.
    
    Args:
        texture: Soil texture class (clayey/sandy/silty/loamy)
    
    Returns:
        Description string
    """
    descriptions = {
        "clayey": "High clay content - good water retention, slower drainage",
        "sandy": "High sand content - fast drainage, less water retention",
        "silty": "High silt content - smooth texture, moderate water retention",
        "loamy": "Balanced mix - ideal for most crops, good water retention and drainage"
    }
    return descriptions.get(texture, "Unknown soil texture")


# Example usage
if __name__ == "__main__":
    # Example coordinates (Kerala, India)
    lat = 10.8505
    lon = 76.2711
    
    print(f"Fetching soil data for coordinates: {lat}, {lon}")
    print("-" * 60)
    
    try:
        soil_data = fetch_soil_data(lat, lon)
        
        print("Soil Properties:")
        print(f"  pH:          {soil_data['soil_ph']}")
        print(f"  Clay:        {soil_data['clay']}%")
        print(f"  Sand:        {soil_data['sand']}%")
        print(f"  Silt:        {soil_data['silt']}%")
        print(f"  Texture:     {soil_data['soil_texture']}")
        print()
        print(f"Description: {get_soil_texture_description(soil_data['soil_texture'])}")
        
    except (SoilGridsError, ValueError) as e:
        print(f"Error: {e}")
