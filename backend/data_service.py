"""
Data service module for QLD Shed & Patio Approval Checker
This module connects to QLD property and planning data services.
"""
import os
import requests
import json
from urllib.parse import quote

# Configuration - Store these securely in environment variables in production
API_KEY = os.environ.get('QLD_SPATIAL_API_KEY', 'your_api_key_here')
PROPERTY_ADDRESS_ENDPOINT = "https://spatial-gis.information.qld.gov.au/arcgis/rest/services/PlanningCadastre/LandParcelPropertyFramework/MapServer/0/query"
PLANNING_SCHEME_ENDPOINT = "https://spatial-gis.information.qld.gov.au/arcgis/rest/services/PlanningCadastre/QldPlanningScheme/MapServer/query"

def geocode_address(address):
    """
    Convert a Queensland address to coordinates using QLD Property Address dataset
    
    Args:
        address (str): A Queensland address
        
    Returns:
        dict: Containing latitude, longitude if successful, None otherwise
    """
    try:
        # URL encode the address
        encoded_address = quote(address)
        
        # Prepare the API request
        params = {
            'where': f"ADDRESS like '{encoded_address}%'",
            'outFields': 'ADDRESS,LATITUDE,LONGITUDE,LOT_PLAN,LGA_NAME',
            'returnGeometry': 'true',
            'f': 'json',
            'token': API_KEY
        }
        
        # Make the API request
        response = requests.get(PROPERTY_ADDRESS_ENDPOINT, params=params)
        data = response.json()
        
        # Check if we got valid results
        if 'features' in data and len(data['features']) > 0:
            # Extract the first matching result
            feature = data['features'][0]
            attributes = feature['attributes']
            
            return {
                'latitude': attributes.get('LATITUDE'),
                'longitude': attributes.get('LONGITUDE'),
                'lot_plan': attributes.get('LOT_PLAN'),
                'lga': attributes.get('LGA_NAME')
            }
        else:
            print(f"No matching addresses found for: {address}")
            return None
            
    except Exception as e:
        print(f"Error geocoding address: {str(e)}")
        return None

def get_property_zone(address):
    """
    Get property zoning information based on address using QLD spatial data services
    
    Args:
        address (str): A Queensland address
        
    Returns:
        str: Zone name or default if not found
    """
    try:
        # Step 1: Geocode the address to get coordinates
        location = geocode_address(address)
        if not location:
            print(f"Unable to geocode address: {address}")
            return "LDR - Low Density Residential"  # Default fallback
        
        # Step 2: Query the zoning information using coordinates
        params = {
            'geometry': f"{location['longitude']},{location['latitude']}",
            'geometryType': 'esriGeometryPoint',
            'inSR': '4326',  # WGS84
            'outFields': 'ZONE_CODE,ZONE_DESCRIPTION,PLANNING_SCHEME_NAME,LGA_NAME',
            'returnGeometry': 'false',
            'f': 'json',
            'token': API_KEY
        }
        
        response = requests.get(PLANNING_SCHEME_ENDPOINT, params=params)
        data = response.json()
        
        # Check if we got valid results
        if 'features' in data and len(data['features']) > 0:
            # Extract the first matching result
            feature = data['features'][0]
            attributes = feature['attributes']
            
            zone_code = attributes.get('ZONE_CODE', '')
            zone_desc = attributes.get('ZONE_DESCRIPTION', '')
            
            return f"{zone_code} - {zone_desc}"
        else:
            print(f"No zoning information found for: {address}")
            return "LDR - Low Density Residential"  # Default fallback
            
    except Exception as e:
        print(f"Error getting property zone: {str(e)}")
        return "LDR - Low Density Residential"  # Default fallback

def get_property_overlays(address):
    """
    Get property overlays based on address using QLD spatial data services
    
    Args:
        address (str): A Queensland address
        
    Returns:
        list: List of overlay dictionaries with name and active status
    """
    # Initialize all overlays as inactive
    overlays = [
        {'name': 'Flood Hazard', 'active': False},
        {'name': 'Bushfire Risk', 'active': False},
        {'name': 'Heritage', 'active': False},
        {'name': 'Environmental Significance', 'active': False},
        {'name': 'Waterway Corridor', 'active': False},
        {'name': 'Landslide Hazard', 'active': False},
    ]
    
    try:
        # Step 1: Geocode the address to get coordinates
        location = geocode_address(address)
        if not location:
            return overlays  # Return default overlays if geocoding fails
        
        # Step 2: For each overlay type, query the corresponding service
        overlay_endpoints = {
            'Flood Hazard': 'https://spatial-gis.information.qld.gov.au/arcgis/rest/services/PlanningCadastre/SPP_FloodHazard/MapServer/query',
            'Bushfire Risk': 'https://spatial-gis.information.qld.gov.au/arcgis/rest/services/PlanningCadastre/SPP_BushfireHazard/MapServer/query',
            'Heritage': 'https://spatial-gis.information.qld.gov.au/arcgis/rest/services/PlanningCadastre/QldHeritage/MapServer/query',
            'Environmental Significance': 'https://spatial-gis.information.qld.gov.au/arcgis/rest/services/PlanningCadastre/SPP_MSES/MapServer/query',
            'Waterway Corridor': 'https://spatial-gis.information.qld.gov.au/arcgis/rest/services/PlanningCadastre/WaterResourceCatchments/MapServer/query',
            'Landslide Hazard': 'https://spatial-gis.information.qld.gov.au/arcgis/rest/services/PlanningCadastre/SPP_LandslideHazard/MapServer/query'
        }
        
        for i, (overlay_name, endpoint) in enumerate(overlay_endpoints.items()):
            params = {
                'geometry': f"{location['longitude']},{location['latitude']}",
                'geometryType': 'esriGeometryPoint',
                'inSR': '4326',  # WGS84
                'outFields': '*',
                'returnGeometry': 'false',
                'f': 'json',
                'token': API_KEY
            }
            
            try:
                response = requests.get(endpoint, params=params)
                data = response.json()
                
                # Check if we got valid results
                if 'features' in data and len(data['features']) > 0:
                    overlays[i]['active'] = True
            except Exception as e:
                print(f"Error checking {overlay_name} overlay: {str(e)}")
                continue
                
        return overlays
            
    except Exception as e:
        print(f"Error getting property overlays: {str(e)}")
        return overlays  # Return default overlays on error

def get_lga_planning_rules(lga_name, structure_type):
    """
    Get the specific planning rules for a structure type in a given LGA
    
    This would connect to a database of planning rules for each LGA
    For now, we'll use simplified logic
    """
    # This would be replaced with actual planning scheme rules
    # Simplified for demonstration
    lga_rules = {
        'BRISBANE CITY': {
            'shed': {'size_limit': 10, 'height_limit': 2.4, 'setback': 1.5},
            'patio': {'size_limit': 10, 'height_limit': 2.7, 'setback': 1.5},
            'carport': {'size_limit': 20, 'height_limit': 2.7, 'setback': 1.5},
            'granny_flat': {'size_limit': 80, 'height_limit': 4.5, 'setback': 3.0}
        },
        'GOLD COAST CITY': {
            'shed': {'size_limit': 10, 'height_limit': 2.4, 'setback': 1.5},
            'patio': {'size_limit': 10, 'height_limit': 2.7, 'setback': 1.5},
            'carport': {'size_limit': 20, 'height_limit': 2.7, 'setback': 1.5},
            'granny_flat': {'size_limit': 60, 'height_limit': 4.5, 'setback': 3.0}
        },
        # Add more LGAs as needed
    }
    
    # Default rules if LGA not found
    default_rules = {
        'shed': {'size_limit': 10, 'height_limit': 2.4, 'setback': 1.5},
        'patio': {'size_limit': 10, 'height_limit': 2.7, 'setback': 1.5},
        'carport': {'size_limit': 20, 'height_limit': 2.7, 'setback': 1.5},
        'granny_flat': {'size_limit': 70, 'height_limit': 4.5, 'setback': 3.0}
    }
    
    # Get rules for the LGA or use default
    lga_specific_rules = lga_rules.get(lga_name.upper(), default_rules)
    
    # Return rules for the specific structure type or default rules
    return lga_specific_rules.get(structure_type, default_rules.get(structure_type, {}))

def get_approval_requirements(zone, overlays, structure_type, address=None):
    """
    Get approval requirements based on zone, overlays, and structure type
    
    Args:
        zone (str): Property zone
        overlays (list): List of overlay dictionaries
        structure_type (str): Type of structure
        address (str, optional): Property address for additional checks
        
    Returns:
        list: List of requirement dictionaries
    """
    requirements = [
        {'name': 'Development Application', 'required': False, 'note': None},
        {'name': 'Building Approval', 'required': False, 'note': None},
        {'name': 'Plumbing Approval', 'required': False, 'note': None},
        {'name': 'Engineering Certificate', 'required': False, 'note': None},
        {'name': 'Overlay Assessment', 'required': False, 'note': None},
    ]
    
    # Get active overlays
    active_overlays = [overlay for overlay in overlays if overlay['active']]
    
    # Get LGA if address provided
    lga_name = None
    if address:
        location = geocode_address(address)
        if location:
            lga_name = location.get('lga')
    
    # Get planning rules for the structure type
    planning_rules = get_lga_planning_rules(lga_name, structure_type) if lga_name else {}
    
    # For demonstration purposes, we'll use a dummy structure size
    # In a real application, this would come from user input
    dummy_size = 100 if structure_type == 'shed' else 50
    
    # Logic for Development Application
    if structure_type == 'granny_flat':
        requirements[0]['required'] = True
        requirements[0]['note'] = "Secondary dwellings typically require development approval in QLD."
    elif structure_type == 'shed' and 'RU' in zone:
        if dummy_size > (planning_rules.get('size_limit', 10) * 10):  # Using a variable for size comparison
            requirements[0]['required'] = True
            requirements[0]['note'] = "Large sheds in rural zones may require development approval."
    elif active_overlays:
        requirements[0]['required'] = True
        requirements[0]['note'] = f"Required due to {', '.join([o['name'] for o in active_overlays])} overlays."
    
    # Logic for Building Approval
    if structure_type in ['shed', 'patio', 'carport'] and dummy_size > planning_rules.get('size_limit', 10):
        requirements[1]['required'] = True
        requirements[1]['note'] = f"Required for structures over {planning_rules.get('size_limit', 10)} square meters."
    elif structure_type == 'granny_flat':
        requirements[1]['required'] = True
        requirements[1]['note'] = "All habitable structures require building approval."
    
    # Logic for Plumbing Approval
    if structure_type == 'granny_flat':
        requirements[2]['required'] = True
        requirements[2]['note'] = "Required for any structure with water or sewer connections."
    
    # Logic for Engineering Certificate
    if structure_type in ['shed', 'patio', 'carport'] and dummy_size > (planning_rules.get('size_limit', 10) * 2):
        requirements[3]['required'] = True
        requirements[3]['note'] = "Required for larger structures to ensure structural integrity."
    elif any(overlay['name'] in ['Flood Hazard', 'Landslide Hazard'] and overlay['active'] for overlay in overlays):
        requirements[3]['required'] = True
        requirements[3]['note'] = "Required due to hazard overlays on the property."
    
    # Logic for Overlay Assessment
    if active_overlays:
        requirements[4]['required'] = True
        overlay_names = ', '.join([o['name'] for o in active_overlays])
        requirements[4]['note'] = f"Required due to {overlay_names} overlays on the property."
    
    return requirements