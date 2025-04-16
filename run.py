"""
Run script for QLD Shed & Patio Approval Checker
Simple entry point to start the Flask application
"""
import os
import sys

# Add the backend directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

# Import the Flask app
from app import app

if __name__ == '__main__':
    # Check if temp directory exists, create if it doesn't
    temp_dir = os.path.join(os.path.dirname(__file__), 'backend', 'temp')
    if not os.path.exists(temp_dir):
        os.makedirs(temp_dir)
        print(f"Created temp directory at {temp_dir}")
    
    # Start the Flask app
    app.run(debug=True, host='0.0.0.0', port=5000)
    print("Server running at http://localhost:5000")