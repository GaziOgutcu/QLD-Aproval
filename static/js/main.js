document.addEventListener('DOMContentLoaded', function() {
    // Set current year in the footer
    document.getElementById('current-year').textContent = new Date().getFullYear();
    
    // Get DOM elements
    const addressInput = document.getElementById('address');
    const structureTypeSelect = document.getElementById('structure-type');
    const checkButton = document.getElementById('check-btn');
    const downloadButton = document.getElementById('download-pdf');
    const resultsDiv = document.getElementById('results');
    const resultsContent = document.getElementById('results-content');
    const errorMessage = document.getElementById('error-message');
    
    // Store approval data for PDF generation
    let approvalData = null;
    
    // Add event listener to the check button
    checkButton.addEventListener('click', async function() {
        // Clear previous error messages
        errorMessage.style.display = 'none';
        
        // Get form values
        const address = addressInput.value.trim();
        const structureType = structureTypeSelect.value;
        
        // Form validation
        if (!address) {
            showError('Please enter a valid property address');
            return;
        }
        
        if (!structureType) {
            showError('Please select a structure type');
            return;
        }
        
        // Show loading state
        checkButton.disabled = true;
        checkButton.textContent = 'Checking...';
        
        try {
            // Send request to the API
            const response = await fetch('/api/check-approval', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ address, structureType }),
            });
            
            if (!response.ok) {
                throw new Error('Failed to fetch approval requirements');
            }
            
            // Parse the response
            approvalData = await response.json();
            
            // Display the results
            displayResults(approvalData, address, structureType);
            
            // Scroll to results
            resultsDiv.scrollIntoView({ behavior: 'smooth' });
            
        } catch (error) {
            showError(error.message);
            resultsDiv.style.display = 'none';
        } finally {
            // Reset button state
            checkButton.disabled = false;
            checkButton.textContent = 'Check Requirements';
        }
    });
    
    // Add event listener to the download button
    downloadButton.addEventListener('click', async function() {
        if (!approvalData) return;
        
        const address = addressInput.value.trim();
        const structureType = structureTypeSelect.value;
        
        try {
            downloadButton.disabled = true;
            downloadButton.textContent = 'Generating PDF...';
            
            const response = await fetch('/api/generate-pdf', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ 
                    address, 
                    structureType, 
                    approvalData 
                }),
            });
            
            if (!response.ok) {
                throw new Error('Failed to generate PDF');
            }
            
            // Create a blob from the PDF Stream
            const blob = await response.blob();
            
            // Create a link element, use it to download the blob, then remove it
            const link = document.createElement('a');
            link.href = window.URL.createObjectURL(blob);
            link.download = `QLD-Approval-Check-${structureType}-${Date.now()}.pdf`;
            link.click();
            window.URL.revokeObjectURL(link.href);
            
        } catch (error) {
            showError('Failed to download PDF: ' + error.message);
        } finally {
            downloadButton.disabled = false;
            downloadButton.textContent = 'Download PDF';
        }
    });
    
    // Function to display error messages
    function showError(message) {
        errorMessage.textContent = message;
        errorMessage.style.display = 'block';
    }
    
    // Function to display the approval results
    function displayResults(data, address, structureType) {
        // Show results container
        resultsDiv.style.display = 'block';
        
        // Format structure type for display
        const structureLabels = {
            'shed': 'Shed',
            'patio': 'Patio',
            'carport': 'Carport',
            'granny_flat': 'Granny Flat'
        };
        
        const structureLabel = structureLabels[structureType] || structureType;
        
        // Create HTML content for results
        let html = `
            <div class="property-info">
                <h3>Property Information</h3>
                <p><strong>Address:</strong> ${address}</p>
                <p><strong>Structure Type:</strong> ${structureLabel}</p>
                <p><strong>Zone:</strong> ${data.zone}</p>
            </div>
            
            <div class="overlays-info">
                <h3>Property Overlays</h3>
                <ul>
        `;
        
        // Add overlays
        data.overlays.forEach(overlay => {
            html += `<li>${overlay.name}: <strong>${overlay.active ? 'Yes' : 'No'}</strong></li>`;
        });
        
        html += `
                </ul>
            </div>
            
            <div class="requirements-info">
                <h3>Approval Checklist</h3>
                <ul class="approval-checklist">
        `;
        
        // Add requirements checklist
        data.requirements.forEach(req => {
            const statusClass = req.approved ? 'approved' : 'not-approved';
            const statusIcon = req.approved ? '✓' : '✗';
            
            html += `
                <li class="${statusClass}">
                    <span class="status-icon">${statusIcon}</span>
                    <div class="requirement-details">
                        <strong>${req.name}</strong>
                        <p>${req.description}</p>
                    </div>
                </li>
            `;
        });
        
        html += `
                </ul>
            </div>
            
            <div class="approval-summary">
                <h3>Approval Summary</h3>
                <div class="summary-status ${data.requiresApproval ? 'requires-approval' : 'exempt'}">
                    <span class="status-indicator"></span>
                    <p><strong>${data.requiresApproval ? 'Development Approval Required' : 'Exempt Development'}</strong></p>
                </div>
                <p>${data.summaryText}</p>
            </div>
            
            <div class="next-steps">
                <h3>Next Steps</h3>
                <ul>
        `;
        
        // Add next steps
        data.nextSteps.forEach(step => {
            html += `<li>${step}</li>`;
        });
        
        html += `
                </ul>
                <div class="disclaimer">
                    <p><small>This assessment is based on the information provided and current Queensland planning regulations. This is not a legal document. For official confirmation, please contact your local council.</small></p>
                </div>
            </div>
        `;
        
        // Update the results content
        resultsContent.innerHTML = html;
        
        // Show or hide download button based on approval data
        downloadButton.style.display = 'block';
    }
    
    // Initialize tooltips if any
    const tooltips = document.querySelectorAll('.tooltip');
    if (tooltips.length > 0) {
        tooltips.forEach(tooltip => {
            tooltip.addEventListener('mouseenter', function() {
                this.querySelector('.tooltip-text').style.display = 'block';
            });
            
            tooltip.addEventListener('mouseleave', function() {
                this.querySelector('.tooltip-text').style.display = 'none';
            });
        });
    }
    
    // Reset form function
    window.resetForm = function() {
        addressInput.value = '';
        structureTypeSelect.value = '';
        resultsDiv.style.display = 'none';
        errorMessage.style.display = 'none';
        approvalData = null;
    }
});