"""
Data service module for QLD Shed & Patio Approval Checker
This module provides dummy data functions that simulate property zoning and overlay lookups.
In a production environment, these would connect to real QLD property databases.
"""

def get_property_zone(address):
    """
    Get property zoning information based on address
    
    For demo purposes, this returns a dummy zone based on the address string.
    """
    # Dummy logic to determine zone based on address
    address_lower = address.lower()
    
    if 'brisbane' in address_lower:
        return 'LDR - Low Density Residential'
    elif 'gold coast' in address_lower:
        return 'MDR - Medium Density Residential'
    elif 'sunshine coast' in address_lower:
        return 'HDR - High Density Residential'
    elif 'rural' in address_lower or 'ipswich' in address_lower:
        return 'RU - Rural Zone'
    elif 'commercial' in address_lower or 'business' in address_lower:
        return 'COM - Commercial Zone'
    elif 'industrial' in address_lower:
        return 'IND - Industrial Zone'
    else:
        return 'LDR - Low Density Residential'  # Default zone

def get_property_overlays(address):
    """
    Get property overlays based on address
    
    For demo purposes, this returns dummy overlays based on the address string.
    """
    address_lower = address.lower()
    
    # Initialize all overlays as inactive
    overlays = [
        {'name': 'Flood Hazard', 'active': False},
        {'name': 'Bushfire Risk', 'active': False},
        {'name': 'Heritage', 'active': False},
        {'name': 'Environmental Significance', 'active': False},
        {'name': 'Waterway Corridor', 'active': False},
        {'name': 'Landslide Hazard', 'active': False},
    ]
    
    # Activate overlays based on keywords in the address
    if any(word in address_lower for word in ['river', 'creek', 'brook', 'water']):
        overlays[0]['active'] = True  # Flood Hazard
        overlays[4]['active'] = True  # Waterway Corridor
    
    if any(word in address_lower for word in ['forest', 'bush', 'wood', 'mountain']):
        overlays[1]['active'] = True  # Bushfire Risk
        overlays[3]['active'] = True  # Environmental Significance
    
    if any(word in address_lower for word in ['historic', 'heritage', 'colonial', 'queenslander']):
        overlays[2]['active'] = True  # Heritage
    
    if any(word in address_lower for word in ['hill', 'slope', 'mount', 'cliff']):
        overlays[5]['active'] = True  # Landslide Hazard
    
    return overlays

def get_approval_requirements(zone, overlays, structure_type):
    """
    Get approval requirements based on zone, overlays, and structure type
    
    This function implements dummy logic to determine what approvals are needed.
    In a real implementation, this would apply actual QLD planning scheme rules.
    """
    requirements = [
        {'name': 'Development Application', 'required': False, 'note': None},
        {'name': 'Building Approval', 'required': False, 'note': None},
        {'name': 'Plumbing Approval', 'required': False, 'note': None},
        {'name': 'Engineering Certificate', 'required': False, 'note': None},
        {'name': 'Overlay Assessment', 'required': False, 'note': None},
    ]
    
    active_overlays = [overlay for overlay in overlays if overlay['active']]
    
    # For demonstration purposes, we'll use a dummy structure size
    # In a real application, this would come from user input
    dummy_size = 100 if structure_type == 'shed' else 50
    
    # Logic for Development Application
    if structure_type == 'granny_flat':
        requirements[0]['required'] = True
        requirements[0]['note'] = "Secondary dwellings typically require development approval in QLD."
    elif structure_type == 'shed' and 'RU' in zone:
        if dummy_size > 100:  # Using a variable for size comparison
            requirements[0]['required'] = True
            requirements[0]['note'] = "Large sheds in rural zones may require development approval."
    elif active_overlays:
        requirements[0]['required'] = True
        requirements[0]['note'] = f"Required due to {', '.join([o['name'] for o in active_overlays])} overlays."
    
    # Logic for Building Approval
    if structure_type in ['shed', 'patio', 'carport'] and dummy_size > 10:  # Using a variable
        requirements[1]['required'] = True
        requirements[1]['note'] = "Required for structures over 10 square meters."
    elif structure_type == 'granny_flat':
        requirements[1]['required'] = True
        requirements[1]['note'] = "All habitable structures require building approval."
    
    # Logic for Plumbing Approval
    if structure_type == 'granny_flat':
        requirements[2]['required'] = True
        requirements[2]['note'] = "Required for any structure with water or sewer connections."
    
    # Logic for Engineering Certificate
    if structure_type in ['shed', 'patio', 'carport'] and dummy_size > 20:  # Using a variable
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