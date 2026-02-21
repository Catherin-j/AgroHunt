"""
SoilGrids API Integration Module

This module provides functions to fetch and process soil properties
from the SoilGrids v2.0 REST API without requiring an API key.

Note: Uses 0-5cm depth as specified by SoilGrids fixed depth intervals.
For 0-30cm range, you could average multiple depths (0-5cm, 5-15cm, 15-30cm).

Functions:
    fetch_soil_properties: Fetch soil data from SoilGrids API
    parse_soil_response: Extract mean values from API response
    classify_soil_texture: Determine soil texture class from percentages
    get_soil_data: Main function to get complete soil information
"""

import requests
from typing import Dict, Optional, Tuple


# SoilGrids API Configuration
SOILGRIDS_BASE_URL = "https://rest.isric.org/soilgrids/v2.0/properties/query"
SOIL_PROPERTIES = ["phh2o", "clay", "sand", "silt"]
# Valid SoilGrids depth ranges: 0-5cm, 5-15cm, 15-30cm, 30-60cm, 60-100cm, 100-200cm
DEPTH_RANGE = "0-5cm"  # Using shallow depth for 0-30cm approximation


def fetch_soil_properties(latitude: float, longitude: float, 
                         properties: list = None, 
                         depth: str = DEPTH_RANGE) -> Optional[Dict]:
    """
    Fetch soil properties from SoilGrids REST API.
    
    Args:
        latitude: Latitude coordinate (-90 to 90)
        longitude: Longitude coordinate (-180 to 180)
        properties: List of soil properties to fetch (default: phh2o, clay, sand, silt)
        depth: Depth range in format "X-Ycm" (default: "0-5cm")
               Valid ranges: 0-5cm, 5-15cm, 15-30cm, 30-60cm, 60-100cm, 100-200cm
    
    Returns:
        Dictionary containing the API response, or None if request fails
    
    Raises:
        ValueError: If coordinates are out of valid range
    """
    # Validate coordinates
    if not (-90 <= latitude <= 90):
        raise ValueError(f"Latitude must be between -90 and 90, got {latitude}")
    if not (-180 <= longitude <= 180):
        raise ValueError(f"Longitude must be between -180 and 180, got {longitude}")
    
    # Use default properties if none provided
    if properties is None:
        properties = SOIL_PROPERTIES
    
    # Build query parameters
    # Note: property needs to be repeated for each property, not as a list
    params = [
        ("lat", latitude),
        ("lon", longitude),
    ]
    
    # Add each property as a separate parameter
    for prop in properties:
        params.append(("property", prop))
    
    # Add depth last
    params.append(("depth", depth))
    
    try:
        # Make API request
        response = requests.get(SOILGRIDS_BASE_URL, params=params, timeout=30)
        response.raise_for_status()
        return response.json()
    
    except requests.exceptions.RequestException as e:
        print(f"Error fetching soil data: {e}")
        return None


def parse_soil_response(response: Dict, depth: str = DEPTH_RANGE) -> Dict[str, float]:
    """
    Parse SoilGrids API response and extract mean values for specified depth.
    
    Args:
        response: JSON response from SoilGrids API
        depth: Depth range to extract (default: "0-5cm")
    
    Returns:
        Dictionary with property names and their mean values
        - phh2o: pH value (scaled by 10, e.g., 65 = pH 6.5)
        - clay/sand/silt: percentage values (g/kg, e.g., 250 = 25%)
    """
    parsed_data = {}
    
    # Check if response has properties and layers
    if not response or "properties" not in response:
        return parsed_data
    
    properties = response["properties"]
    layers = properties.get("layers", [])
    
    # Each layer is a dictionary with 'name' and 'depths'
    for layer in layers:
        if not isinstance(layer, dict):
            continue
        
        prop_name = layer.get("name")
        if not prop_name:
            continue
        
        # Find the depth layer we're interested in
        depths = layer.get("depths", [])
        for depth_item in depths:
            if depth_item.get("label") == depth:
                values = depth_item.get("values", {})
                mean_value = values.get("mean")
                if mean_value is not None:
                    parsed_data[prop_name] = mean_value
                break
    
    return parsed_data


def classify_soil_texture(clay: float, sand: float, silt: float) -> str:
    """
    Classify soil texture based on clay, sand, and silt percentages.
    
    Uses simplified USDA soil texture classification rules:
    - Clayey: clay > 40%
    - Sandy: sand > 70% 
    - Silty: silt > 60%
    - Loamy: all other combinations (balanced mixture)
    
    Args:
        clay: Clay percentage (0-100)
        sand: Sand percentage (0-100)
        silt: Silt percentage (0-100)
    
    Returns:
        String indicating soil texture class: "clayey", "sandy", "silty", or "loamy"
    """
    # Normalize percentages to ensure they sum to 100
    total = clay + sand + silt
    if total > 0:
        clay_pct = (clay / total) * 100
        sand_pct = (sand / total) * 100
        silt_pct = (silt / total) * 100
    else:
        return "unknown"
    
    # Apply classification rules
    if clay_pct > 40:
        return "clayey"
    elif sand_pct > 70:
        return "sandy"
    elif silt_pct > 60:
        return "silty"
    else:
        return "loamy"


def get_soil_data(latitude: float, longitude: float) -> Dict[str, any]:
    """
    Get complete soil information for a given location.
    
    This is the main function that orchestrates fetching, parsing,
    and classifying soil data from SoilGrids.
    
    Args:
        latitude: Latitude coordinate (-90 to 90)
        longitude: Longitude coordinate (-180 to 180)
    
    Returns:
        Dictionary containing:
            - soil_ph: Soil pH value (float)
            - clay: Clay percentage (float, 0-100)
            - sand: Sand percentage (float, 0-100)
            - silt: Silt percentage (float, 0-100)
            - soil_texture: Texture classification (string)
        
        Returns empty dict if data cannot be retrieved.
    """
    # Fetch data from API
    response = fetch_soil_properties(latitude, longitude)
    if not response:
        return {}
    
    # Parse the response
    parsed = parse_soil_response(response)
    if not parsed:
        return {}
    
    # Convert raw values to user-friendly format
    result = {}
    
    # pH: API returns pH * 10 (e.g., 65 = pH 6.5)
    if "phh2o" in parsed:
        result["soil_ph"] = parsed["phh2o"] / 10.0
    
    # Clay, Sand, Silt: API returns g/kg, convert to percentage
    clay_val = parsed.get("clay", 0) / 10.0  # g/kg to percentage
    sand_val = parsed.get("sand", 0) / 10.0
    silt_val = parsed.get("silt", 0) / 10.0
    
    result["clay"] = clay_val
    result["sand"] = sand_val
    result["silt"] = silt_val
    
    # Classify soil texture
    if clay_val or sand_val or silt_val:
        result["soil_texture"] = classify_soil_texture(clay_val, sand_val, silt_val)
    else:
        result["soil_texture"] = "unknown"
    
    return result


# Example usage
if __name__ == "__main__":
    # Example coordinates (Iowa, USA - agricultural area)
    test_lat = 41.5
    test_lon = -93.5
    
    print(f"Fetching soil data for coordinates: ({test_lat}, {test_lon})")
    print("-" * 60)
    
    # Get soil data
    soil_data = get_soil_data(test_lat, test_lon)
    
    if soil_data:
        print("Soil Properties:")
        print(f"  pH: {soil_data.get('soil_ph', 'N/A')}")
        print(f"  Clay: {soil_data.get('clay', 'N/A'):.1f}%")
        print(f"  Sand: {soil_data.get('sand', 'N/A'):.1f}%")
        print(f"  Silt: {soil_data.get('silt', 'N/A'):.1f}%")
        print(f"  Texture: {soil_data.get('soil_texture', 'N/A')}")
    else:
        print("Failed to retrieve soil data (location may have no coverage)")
    
    print("-" * 60)
    
    # Example with different location (Spain - farmland)
    test_lat2 = 40.0
    test_lon2 = -3.0
    
    print(f"\nFetching soil data for coordinates: ({test_lat2}, {test_lon2})")
    print("-" * 60)
    
    soil_data2 = get_soil_data(test_lat2, test_lon2)
    
    if soil_data2:
        print("Soil Properties:")
        print(f"  pH: {soil_data2.get('soil_ph', 'N/A')}")
        print(f"  Clay: {soil_data2.get('clay', 'N/A'):.1f}%")
        print(f"  Sand: {soil_data2.get('sand', 'N/A'):.1f}%")
        print(f"  Silt: {soil_data2.get('silt', 'N/A'):.1f}%")
        print(f"  Texture: {soil_data2.get('soil_texture', 'N/A')}")
    else:
        print("Failed to retrieve soil data (location may have no coverage)")
