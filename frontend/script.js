// Global variables
let currentJobId = null;
let progressInterval = null;
let currentResults = [];

// DOM elements
const fileUploadArea = document.getElementById('fileUploadArea');
const csvFileInput = document.getElementById('csvFileInput');
const fileInfo = document.getElementById('fileInfo');
const fileName = document.getElementById('fileName');
const fileSize = document.getElementById('fileSize');
const uploadBtn = document.getElementById('uploadBtn');
const uploadSection = document.getElementById('uploadSection');
const progressSection = document.getElementById('progressSection');
const resultsSection = document.getElementById('resultsSection');
const progressFill = document.getElementById('progressFill');
const progressText = document.getElementById('progressText');
const progressPercentage = document.getElementById('progressPercentage');
const estimatedTime = document.getElementById('estimatedTime');
const processingStatus = document.getElementById('processingStatus');
const downloadBtn = document.getElementById('downloadBtn');
const newUploadBtn = document.getElementById('newUploadBtn');
const resultsTableBody = document.getElementById('resultsTableBody');
const searchInput = document.getElementById('searchInput');
const totalBusinesses = document.getElementById('totalBusinesses');
const totalContacts = document.getElementById('totalContacts');
const successRate = document.getElementById('successRate');
const loadingOverlay = document.getElementById('loadingOverlay');
const errorModal = document.getElementById('errorModal');
const errorMessage = document.getElementById('errorMessage');

// Initialize event listeners
document.addEventListener('DOMContentLoaded', function() {
    initializeEventListeners();
});

function initializeEventListeners() {
    // File input change
    csvFileInput.addEventListener('change', handleFileSelect);
    
    // Drag and drop
    fileUploadArea.addEventListener('dragover', handleDragOver);
    fileUploadArea.addEventListener('dragleave', handleDragLeave);
    fileUploadArea.addEventListener('drop', handleDrop);
    
    // Upload button
    uploadBtn.addEventListener('click', uploadFile);
    
    // Download button
    downloadBtn.addEventListener('click', downloadResults);
    
    // New upload button
    newUploadBtn.addEventListener('click', resetToUpload);
    
    // Search input
    searchInput.addEventListener('input', filterResults);
}

// File handling functions
function handleFileSelect(event) {
    const file = event.target.files[0];
    if (file) {
        displayFileInfo(file);
    }
}

function handleDragOver(event) {
    event.preventDefault();
    fileUploadArea.classList.add('dragover');
}

function handleDragLeave(event) {
    event.preventDefault();
    fileUploadArea.classList.remove('dragover');
}

function handleDrop(event) {
    event.preventDefault();
    fileUploadArea.classList.remove('dragover');
    
    const files = event.dataTransfer.files;
    if (files.length > 0) {
        const file = files[0];
        if (file.type === 'text/csv' || file.name.endsWith('.csv')) {
            csvFileInput.files = files;
            displayFileInfo(file);
        } else {
            showError('Please select a CSV file.');
        }
    }
}

function displayFileInfo(file) {
    fileName.textContent = file.name;
    fileSize.textContent = formatFileSize(file.size);
    fileInfo.style.display = 'flex';
}

function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

async function uploadFile() {
    const file = csvFileInput.files[0];
    if (!file) {
        showError('Please select a file first.');
        return;
    }

    showLoading(true);

    const formData = new FormData();
    formData.append('file', file);

    try {
        const response = await fetch('/upload', {
            method: 'POST',
            body: formData
        });

        // Check if response is JSON
        const contentType = response.headers.get('content-type');
        if (!contentType || !contentType.includes('application/json')) {
            const textResponse = await response.text();
            throw new Error(`Server returned non-JSON response: ${textResponse.substring(0, 200)}`);
        }

        const result = await response.json();
        
        if (response.ok) {
            currentJobId = result.job_id;
            console.log('Upload successful, job ID:', currentJobId);
            showProgress();
            startProgressTracking();
        } else {
            throw new Error(result.detail || 'Upload failed');
        }
    } catch (error) {
        console.error('Upload error:', error);
        showError('Upload failed: ' + error.message);
    } finally {
        showLoading(false);
    }
}


function showProgress() {
    uploadSection.style.display = 'none';
    progressSection.style.display = 'block';
    resultsSection.style.display = 'none';
}

function startProgressTracking() {
    progressInterval = setInterval(checkProgress, 2000);
    checkProgress(); // Check immediately
}

async function checkProgress() {
    if (!currentJobId) return;

    try {
        const response = await fetch(`/status/${currentJobId}`);
        
        // Check if response is JSON
        const contentType = response.headers.get('content-type');
        if (!contentType || !contentType.includes('application/json')) {
            const textResponse = await response.text();
            console.error('Non-JSON response from status endpoint:', textResponse);
            return;
        }

        const status = await response.json();
        console.log('Status update:', status);

        updateProgressDisplay(status);

        if (status.status === 'completed') {
            clearInterval(progressInterval);
            await loadResults();
        } else if (status.status === 'error') {
            clearInterval(progressInterval);
            showError('Processing failed: ' + status.error);
            resetToUpload();
        }
    } catch (error) {
        console.error('Error checking progress:', error);
    }
}

function updateProgressDisplay(status) {
    const progress = status.progress || 0;
    const total = status.total || 0;
    const percentage = total > 0 ? Math.round((progress / total) * 100) : 0;

    progressFill.style.width = `${percentage}%`;
    progressText.textContent = `${progress} / ${total} processed`;
    progressPercentage.textContent = `${percentage}%`;
    processingStatus.textContent = status.status.charAt(0).toUpperCase() + status.status.slice(1);

    // Calculate estimated time
    if (progress > 0 && total > 0) {
        const remainingItems = total - progress;
        const estimatedSeconds = (remainingItems / progress) * 30; // Rough estimate
        estimatedTime.textContent = formatTime(estimatedSeconds);
    }
}

function formatTime(seconds) {
    if (seconds < 60) return Math.round(seconds) + ' seconds';
    if (seconds < 3600) return Math.round(seconds / 60) + ' minutes';
    return Math.round(seconds / 3600) + ' hours';
}

// Results functions
async function loadResults() {
    try {
        const response = await fetch(`/results/${currentJobId}`);
        const results = await response.json();
        
        currentResults = results;
        displayResults(results);
        showResults();
    } catch (error) {
        showError('Failed to load results: ' + error.message);
    }
}

function displayResults(results) {
    // Update summary
    const totalBusinessesCount = results.length;
    const totalContactsCount = results.filter(r => r.contact_numbers && r.contact_numbers.trim()).length;
    const successRateValue = totalBusinessesCount > 0 ? Math.round((totalContactsCount / totalBusinessesCount) * 100) : 0;

    totalBusinesses.textContent = totalBusinessesCount;
    totalContacts.textContent = totalContactsCount;
    successRate.textContent = successRateValue + '%';

    // Populate table
    populateTable(results);
}

function populateTable(results) {
    resultsTableBody.innerHTML = '';

    results.forEach(row => {
        const tr = document.createElement('tr');
        
        // Business Name
        const nameTd = document.createElement('td');
        nameTd.textContent = row.business_name || 'N/A';
        tr.appendChild(nameTd);

        // Business Address
        const addressTd = document.createElement('td');
        addressTd.textContent = row.business_address || 'N/A';
        tr.appendChild(addressTd);

        // Contact Numbers (with highlighting)
        const contactTd = document.createElement('td');
        if (row.contact_numbers && row.contact_numbers.trim()) {
            const contacts = row.contact_numbers.split(',').map(c => c.trim()).filter(c => c);
            contactTd.innerHTML = contacts.map(contact => 
                `<span class="contact-number">${contact}</span>`
            ).join(' ');
        } else {
            contactTd.textContent = 'No contacts found';
            contactTd.style.color = '#a0aec0';
        }
        tr.appendChild(contactTd);

        // Search Resources
        const resourcesTd = document.createElement('td');
        resourcesTd.textContent = row.search_resources || 'N/A';
        tr.appendChild(resourcesTd);

        resultsTableBody.appendChild(tr);
    });
}

function showResults() {
    uploadSection.style.display = 'none';
    progressSection.style.display = 'none';
    resultsSection.style.display = 'block';
}

// Filter and search functions
function filterResults() {
    const searchTerm = searchInput.value.toLowerCase();
    const filteredResults = currentResults.filter(row => {
        return (
            (row.business_name && row.business_name.toLowerCase().includes(searchTerm)) ||
            (row.business_address && row.business_address.toLowerCase().includes(searchTerm)) ||
            (row.contact_numbers && row.contact_numbers.toLowerCase().includes(searchTerm)) ||
            (row.search_resources && row.search_resources.toLowerCase().includes(searchTerm))
        );
    });
    populateTable(filteredResults);
}

// Download and export functions
async function downloadResults() {
    if (!currentJobId) return;

    try {
        const response = await fetch(`/download/${currentJobId}`);
        if (response.ok) {
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `skip_trace_results_${new Date().toISOString().split('T')[0]}.csv`;
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            document.body.removeChild(a);
        } else {
            throw new Error('Download failed');
        }
    } catch (error) {
        showError('Download failed: ' + error.message);
    }
}

function exportToCSV() {
    if (!currentResults.length) return;

    const headers = ['Business Name', 'Business Address', 'Contact Numbers', 'Search Resources'];
    const csvContent = [
        headers.join(','),
        ...currentResults.map(row => [
            `"${(row.business_name || '').replace(/"/g, '""')}"`,
            `"${(row.business_address || '').replace(/"/g, '""')}"`,
            `"${(row.contact_numbers || '').replace(/"/g, '""')}"`,
            `"${(row.search_resources || '').replace(/"/g, '""')}"`
        ].join(','))
    ].join('\n');

    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `filtered_results_${new Date().toISOString().split('T')[0]}.csv`;
    document.body.appendChild(a);
    a.click();
    window.URL.revokeObjectURL(url);
    document.body.removeChild(a);
}

// UI utility functions
function showLoading(show) {
    loadingOverlay.style.display = show ? 'flex' : 'none';
}

function showError(message) {
    errorMessage.textContent = message;
    errorModal.style.display = 'flex';
}

function closeModal() {
    errorModal.style.display = 'none';
}

function resetToUpload() {
    // Clear current state
    currentJobId = null;
    currentResults = [];
    
    // Clear progress interval
    if (progressInterval) {
        clearInterval(progressInterval);
        progressInterval = null;
    }
    
    // Reset file input
    csvFileInput.value = '';
    fileInfo.style.display = 'none';
    
    // Reset progress display
    progressFill.style.width = '0%';
    progressText.textContent = '0 / 0 processed';
    progressPercentage.textContent = '0%';
    estimatedTime.textContent = 'Calculating...';
    processingStatus.textContent = 'Initializing...';
    
    // Reset search
    searchInput.value = '';
    
    // Show upload section
    uploadSection.style.display = 'block';
    progressSection.style.display = 'none';
    resultsSection.style.display = 'none';
}

// Close modal when clicking outside
window.addEventListener('click', function(event) {
    if (event.target === errorModal) {
        closeModal();
    }
});

// Keyboard shortcuts
document.addEventListener('keydown', function(event) {
    // Escape key to close modal
    if (event.key === 'Escape') {
        closeModal();
    }
    
    // Ctrl+N for new upload (when results are shown)
    if (event.ctrlKey && event.key === 'n' && resultsSection.style.display === 'block') {
        event.preventDefault();
        resetToUpload();
    }
});

// Auto-resize search input on mobile
function adjustSearchInput() {
    if (window.innerWidth <= 768) {
        searchInput.style.width = '100%';
    } else {
        searchInput.style.width = '250px';
    }
}

window.addEventListener('resize', adjustSearchInput);
adjustSearchInput(); // Call on load 