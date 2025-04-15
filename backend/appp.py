from flask import Flask, jsonify, request, render_template, send_file
import json
import os
from datetime import datetime
import pdfkit
from werkzeug.middleware.proxy_fix import ProxyFix

app = Flask(__name__, 
            static_folder="./frontend/build/static", 
            template_folder="./frontend/build")

# Apply the proxy fix for proper handling of scheme and host when behind a proxy
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# Import dummy data modules
from data_service import (
    get_property_zone,
    get_property_overlays,
    get_approval_requirements
)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/check-approval', methods=['POST'])
def check_approval():
    """API endpoint to check approval requirements for a property and structure"""
    data = request.json
    address = data.get('address')
    structure_type = data.get('structureType')
    
    if not address or not structure_type:
        return jsonify({'error': 'Address and structure type are required'}), 400
    
    try:
        # Get property zone (dummy data for now)
        zone = get_property_zone(address)
        
        # Get property overlays (dummy data for now)
        overlays = get_property_overlays(address)
        
        # Get approval requirements based on zone, overlays, and structure type
        requirements = get_approval_requirements(zone, overlays, structure_type)
        
        # Generate next steps message
        if any(req['required'] for req in requirements):
            next_steps = (
                "Based on your property's zoning and overlays, you need to apply for approval "
                "for your " + structure_type.replace('_', ' ') + ". Contact your local council for further details."
            )
        else:
            next_steps = (
                "Good news! Based on the information provided, your " + 
                structure_type.replace('_', ' ') + " may not require council approval. "
                "However, we recommend confirming with your local council before proceeding."
            )
        
        result = {
            'zone': zone,
            'overlays': overlays,
            'requirements': requirements,
            'nextSteps': next_steps
        }
        
        return jsonify(result)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/generate-pdf', methods=['POST'])
def generate_pdf():
    """Generate a PDF report of the approval requirements"""
    data = request.json
    address = data.get('address')
    structure_type = data.get('structureType')
    approval_data = data.get('approvalData')
    
    if not address or not structure_type or not approval_data:
        return jsonify({'error': 'Missing required data'}), 400
    
    try:
        # Structure type to display name mapping
        structure_labels = {
            'shed': 'Shed',
            'patio': 'Patio',
            'carport': 'Carport',
            'granny_flat': 'Granny Flat'
        }
        
        structure_label = structure_labels.get(structure_type, structure_type)
        
        # Generate HTML for the PDF
        rendered_html = render_template(
            'pdf_template.html',
            address=address,
            structure_type=structure_label,
            zone=approval_data['zone'],
            overlays=approval_data['overlays'],
            requirements=approval_data['requirements'],
            next_steps=approval_data['nextSteps'],
            date=datetime.now().strftime('%d/%m/%Y')
        )
        
        # Create PDF filename
        filename = f"QLD-Approval-Check-{structure_type}-{datetime.now().strftime('%Y%m%d%H%M%S')}.pdf"
        pdf_path = os.path.join(app.root_path, 'temp', filename)
        
        # Ensure temp directory exists
        os.makedirs(os.path.dirname(pdf_path), exist_ok=True)
        
        # Generate PDF file
        pdfkit.from_string(rendered_html, pdf_path)
        
        # Send the file to the client
        return send_file(
            pdf_path,
            mimetype='application/pdf',
            as_attachment=True,
            download_name=filename
        )
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Add an error handler for 404
@app.errorhandler(404)
def not_found(e):
    # For SPA routing, send index.html for any unmatched routes
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)