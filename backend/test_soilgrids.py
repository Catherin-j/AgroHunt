"""
Test script for SoilGrids integration
Run this to verify the SoilGrids API integration works correctly
"""

import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.soilgrids_service import (
    fetch_soil_data, 
    SoilGridsError, 
    get_soil_texture_description
)


def test_basic_fetch():
    """Test basic soil data fetching."""
    print("=" * 70)
    print("TEST 1: Basic Soil Data Fetch")
    print("=" * 70)
    
    # Test coordinates (Thrissur, Kerala, India)
    lat = 10.5276
    lon = 76.2144
    
    print(f"\nFetching soil data for: {lat}, {lon}")
    print(f"Location: Thrissur, Kerala, India\n")
    
    try:
        soil_data = fetch_soil_data(lat, lon)
        
        source_icon = "✓" if soil_data.get('source') == 'soilgrids' else "⚠"
        print(f"{source_icon} {'Success' if soil_data.get('source') == 'soilgrids' else 'Using Fallback Data'}!")
        
        if soil_data.get('source') == 'fallback':
            print(f"  Note: {soil_data.get('note', 'API unavailable')}\n")
        
        print("Soil Properties:")
        print(f"  pH:          {soil_data['soil_ph']}")
        print(f"  Clay:        {soil_data['clay']}%")
        print(f"  Sand:        {soil_data['sand']}%")
        print(f"  Silt:        {soil_data['silt']}%")
        print(f"  Texture:     {soil_data['soil_texture']}")
        print(f"  Source:      {soil_data.get('source', 'unknown')}")
        
        description = get_soil_texture_description(soil_data['soil_texture'])
        print(f"\n  Description: {description}")
        
        return True
        
    except Exception as e:
        print(f"✗ Failed: {e}")
        return False


def test_multiple_locations():
    """Test multiple locations around the world."""
    print("\n" + "=" * 70)
    print("TEST 2: Multiple Locations")
    print("=" * 70 + "\n")
    
    locations = [
        {"name": "Iowa, USA (Farm Belt)", "lat": 42.0, "lon": -93.5},
        {"name": "Kerala, India", "lat": 10.8505, "lon": 76.2711},
        {"name": "Punjab, India", "lat": 31.1471, "lon": 75.3412},
        {"name": "Netherlands", "lat": 52.1326, "lon": 5.2913},
    ]
    
    for location in locations:
        print(f"Testing: {location['name']}")
        try:
            soil_data = fetch_soil_data(location['lat'], location['lon'])
            source = "✓" if soil_data.get('source') == 'soilgrids' else "⚠"
            print(f"  {source} pH: {soil_data['soil_ph']}, "
                  f"Texture: {soil_data['soil_texture']}, "
                  f"Clay: {soil_data['clay']}% "
                  f"[{soil_data.get('source', 'unknown')}]")
        except Exception as e:
            print(f"  ✗ Error: {e}")
        print()


def test_error_handling():
    """Test error handling with invalid inputs."""
    print("=" * 70)
    print("TEST 3: Error Handling")
    print("=" * 70 + "\n")
    
    # Test invalid latitude
    print("Testing invalid latitude (95)...")
    try:
        fetch_soil_data(95, 76.27)
        print("  ✗ Should have raised ValueError")
    except ValueError as e:
        print(f"  ✓ Correctly raised ValueError: {e}\n")
    
    # Test invalid longitude
    print("Testing invalid longitude (200)...")
    try:
        fetch_soil_data(10.85, 200)
        print("  ✗ Should have raised ValueError")
    except ValueError as e:
        print(f"  ✓ Correctly raised ValueError: {e}\n")


def test_texture_classification():
    """Test soil texture classification logic."""
    print("=" * 70)
    print("TEST 4: Texture Classification")
    print("=" * 70 + "\n")
    
    from app.soilgrids_service import _classify_soil_texture
    
    test_cases = [
        {"clay": 45, "sand": 30, "silt": 25, "expected": "clayey"},
        {"clay": 10, "sand": 75, "silt": 15, "expected": "sandy"},
        {"clay": 15, "sand": 20, "silt": 65, "expected": "silty"},
        {"clay": 25, "sand": 40, "silt": 35, "expected": "loamy"},
    ]
    
    for case in test_cases:
        result = _classify_soil_texture(case['clay'], case['sand'], case['silt'])
        status = "✓" if result == case['expected'] else "✗"
        print(f"{status} Clay:{case['clay']}% Sand:{case['sand']}% Silt:{case['silt']}% "
              f"→ {result} (expected: {case['expected']})")


def main():
    """Run all tests."""
    print("\n" + "=" * 70)
    print("SOILGRIDS API INTEGRATION TEST SUITE")
    print("=" * 70 + "\n")
    
    # Run tests
    test_basic_fetch()
    test_multiple_locations()
    test_error_handling()
    test_texture_classification()
    
    print("\n" + "=" * 70)
    print("ALL TESTS COMPLETED")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    main()
