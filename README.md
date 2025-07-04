# ARM Skip Trace - Business Contact Finder

A modern, sleek web application for finding business contact information through intelligent web search using Large Language Models (LLM). Upload a CSV file with business information and get back detailed contact information including phone numbers, addresses, and search resources.

![ARM Skip Trace](https://img.shields.io/badge/Status-Active-green)
![Python](https://img.shields.io/badge/Python-3.8+-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104.1-green)
![License](https://img.shields.io/badge/License-MIT-blue)

## 🌟 Features

### 🎨 **Modern UI/UX**
- **Sleek, minimalistic design** with glassmorphism effects
- **Responsive design** that works on desktop, tablet, and mobile
- **Smooth animations** and transitions
- **Real-time progress tracking** with visual feedback
- **Drag and drop** file upload functionality

### 🔍 **Intelligent Contact Search**
- **AI-powered web search** using OpenAI GPT models
- **Concurrent processing** for fast results (up to 1000 parallel requests)
- **Flexible CSV format** support with multiple column name variations
- **Comprehensive contact extraction** including multiple phone numbers

### 📊 **Advanced Results Display**
- **Interactive data table** with search and filter capabilities
- **Highlighted contact numbers** for easy identification
- **Summary statistics** showing success rates and totals
- **Downloadable CSV results** with original formatting
- **Real-time export** functionality

### ⚡ **Performance & Reliability**
- **Asynchronous processing** for optimal performance
- **Error handling** with user-friendly messages
- **Progress tracking** with estimated completion times
- **Background job processing** with status updates

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- OpenAI API key

### Installation

1. **Clone or download the project files**
2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables:**
   Create a `.env` file in the root directory:
   ```env
   OPENAI_API_KEY=your_openai_api_key_here
   ```

4. **Run the application (Easy Method):**
   ```bash
   python run_app.py
   ```
   This script will automatically:
   - Check all dependencies
   - Verify your environment setup
   - Start the server
   - Open your web browser

   **Or run manually:**
   ```bash
   python backend/main.py
   ```
   Or alternatively:
   ```bash
   uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
   ```

5. **Access the application:**
   Open your browser and navigate to: `http://localhost:8000`

## 📁 Required Dependencies

The application requires the following Python packages (automatically installed with `requirements.txt`):

```txt
openai == 1.93.0          # OpenAI API client for LLM functionality
python-dotenv == 1.1.1    # Environment variable management
fastapi == 0.104.1        # Modern web framework
uvicorn[standard] == 0.24.0  # ASGI server
python-multipart == 0.0.6    # File upload support
pandas == 2.1.4           # Data manipulation and CSV handling
aiofiles == 23.2.1        # Asynchronous file operations
```

## 📊 CSV Format Requirements

Your input CSV file should contain business information with the following supported column names:

### Required Columns (at least one):
- `business_name` or `Business_Name` - Name of the business
- `address` or `Address` - Business address

### Optional Columns:
- `web_page` - Business website URL
- `other_info` - Additional business information

### Example CSV Format:
```csv
Business_Name,Address,web_page,other_info
Balloons Boutique SA,"10828 Gulfdale St Suite B, San Antonio, TX 78216",balloonsboutiquesa.com,Party supplies store
Tech Solutions Inc,"123 Main St, Austin, TX 78701",techsolutions.com,Software development
```

## 🔧 Usage Guide

### 1. **Upload CSV File**
- Drag and drop your CSV file or click "Browse Files"
- File validation ensures CSV format compliance
- Preview file information before processing

### 2. **Processing**
- Real-time progress tracking with animated search indicators
- Estimated completion time calculation
- Concurrent processing for optimal speed

### 3. **View Results**
- **Summary Cards**: Total businesses processed, contacts found, success rate
- **Interactive Table**: Searchable and filterable results
- **Highlighted Contacts**: Multiple phone numbers displayed as badges
- **Download Options**: Get results as CSV file

### 4. **Export & Download**
- Download complete results as CSV
- Export filtered results
- Preserve original data formatting

## 🏗️ Architecture

### Backend (FastAPI)
- **RESTful API** with async/await pattern
- **Background task processing** for long-running operations
- **In-memory job tracking** (scalable to Redis/Database)
- **File handling** with temporary storage
- **CORS enabled** for frontend integration

### Frontend (Vanilla JavaScript)
- **Modern ES6+** JavaScript with async/await
- **Responsive CSS Grid/Flexbox** layouts
- **CSS animations** and transitions
- **Progressive enhancement** design

### Key API Endpoints:
- `POST /upload` - Upload and start processing CSV
- `GET /status/{job_id}` - Check processing status
- `GET /results/{job_id}` - Retrieve processed results
- `GET /download/{job_id}` - Download results as CSV

## 🎨 UI Components

### **Upload Section**
- Drag & drop file upload area
- File validation and preview
- Progress indicators

### **Processing Section**
- Animated search indicators
- Real-time progress bar
- Estimated time remaining
- Processing status updates

### **Results Section**
- Summary statistics cards
- Interactive data table
- Search and filter functionality
- Download and export options

## 🔐 Security Features

- **File type validation** (CSV only)
- **Input sanitization** for CSV data
- **Error handling** with graceful degradation
- **CORS configuration** for secure frontend communication

## 📱 Responsive Design

The application is fully responsive and optimized for:
- **Desktop** (1200px+): Full feature set with optimal layout
- **Tablet** (768px-1199px): Adapted layout with touch-friendly controls
- **Mobile** (320px-767px): Single-column layout with stacked components

## 🔧 Configuration Options

### **Concurrency Settings**
Adjust the `CONCURRENCY_LIMIT` in `backend/main.py`:
```python
CONCURRENCY_LIMIT = 1000  # Reduce if hitting API rate limits
```

### **OpenAI Model Configuration**
Modify the model settings in `WebSearchLLM.py`:
```python
model="gpt-4.1-mini"  # Change model as needed
```

## 🚀 Performance Optimization

### **Concurrent Processing**
- Utilizes asyncio for non-blocking operations
- Configurable concurrency limits
- Efficient memory usage with streaming

### **Frontend Optimization**
- Lazy loading for large result sets
- Debounced search input
- Efficient DOM manipulation

## 🐛 Troubleshooting

### **Common Issues:**

1. **OpenAI API Errors**
   - Ensure valid API key in `.env` file
   - Check API quota and billing status
   - Verify model availability

2. **File Upload Issues**
   - Ensure CSV format compliance
   - Check file size limits
   - Verify required columns exist

3. **Processing Failures**
   - Monitor console for error messages
   - Check network connectivity
   - Verify API rate limits

### **Error Messages:**
- `"Only CSV files are allowed"` - Upload a valid CSV file
- `"CSV must contain required columns"` - Add business_name or address columns
- `"Processing failed"` - Check API key and connectivity

## 🔄 Development Mode

For development with auto-reload:
```bash
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

Enable debug logging by setting:
```python
logging.basicConfig(level=logging.DEBUG)
```

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## How to Fix and Test:
Stop using Live Server - Don't open index.html directly
Update the backend with the fixes above
Start the backend using python run_app.py
Access the app at http://localhost:8000 (not via Live Server)


---

**Built with ❤️ for efficient business contact discovery**

*ARM Skip Trace - Making business contact research fast, accurate, and effortless.* 
