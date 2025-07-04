from fastapi import FastAPI, File, UploadFile, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import asyncio
import uuid
import os
import sys
from typing import Dict, List
import tempfile
import json
from datetime import datetime

# Add parent directory to path to import WebSearchLLM
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# Import with error handling
try:
    from WebSearchLLM import llm_contact_search
    print("✅ Successfully imported WebSearchLLM")
except ImportError as e:
    print(f"❌ Failed to import WebSearchLLM: {e}")
    print("Make sure WebSearchLLM.py is in the parent directory")
    sys.exit(1)

app = FastAPI(title="ARM Skip Trace", description="Web application for business contact skip tracing")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create directories if they don't exist
os.makedirs("temp", exist_ok=True)

# Mount static files - fix the path
frontend_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "frontend")
app.mount("/static", StaticFiles(directory=frontend_path), name="static")

# In-memory storage for job status (in production, use Redis or database)
job_status = {}
results_storage = {}

CONCURRENCY_LIMIT = 1000

async def process_csv_data(job_id: str, df: pd.DataFrame) -> None:
    """Process CSV data with LLM contact search."""
    try:
        job_status[job_id] = {"status": "processing", "progress": 0, "total": len(df)}
        
        semaphore = asyncio.Semaphore(CONCURRENCY_LIMIT)
        
        async def _worker(row: pd.Series, index: int) -> Dict:
            async with semaphore:
                result = await process_row(row)
                # Update progress
                job_status[job_id]["progress"] = index + 1
                return result
        
        tasks = [_worker(row, idx) for idx, (_, row) in enumerate(df.iterrows())]
        results = await asyncio.gather(*tasks, return_exceptions=False)
        
        # Create output DataFrame
        out_df = pd.DataFrame(results, columns=[
            "business_name",
            "business_address", 
            "contact_numbers",
            "search_resources",
        ])
        
        # Save results
        output_filename = f"output_{job_id}.csv"
        output_path = os.path.join("temp", output_filename)
        os.makedirs("temp", exist_ok=True)
        out_df.to_csv(output_path, index=False)
        
        # Store results for API access
        results_storage[job_id] = {
            "data": out_df.to_dict('records'),
            "filename": output_filename,
            "path": output_path
        }
        
        job_status[job_id] = {
            "status": "completed", 
            "progress": len(df), 
            "total": len(df),
            "filename": output_filename
        }
        
    except Exception as e:
        job_status[job_id] = {"status": "error", "error": str(e)}

async def process_row(row: pd.Series) -> Dict:
    """Process a single row from the CSV."""
    prompt_parts = []
    
    if pd.notna(row.get("Business_Name")):
        prompt_parts.append(f"Business Name: {row['Business_Name']}")
    if pd.notna(row.get("Address")):
        prompt_parts.append(f"Address: {row['Address']}")
    if pd.notna(row.get("web_page")):
        prompt_parts.append(f"web_page: {row['web_page']}")
    if pd.notna(row.get("other_info")):
        prompt_parts.append(f"other_info: {row['other_info']}")
    
    prompt = ", ".join(prompt_parts)
    
    try:
        result = await llm_contact_search(prompt)
        return {
            "business_name": result.get("business_name", ""),
            "business_address": result.get("business_address", ""),
            "contact_numbers": ", ".join(result.get("contact_numbers", [])),
            "search_resources": result.get("search_resources", ""),
        }
    except Exception as e:
        return {
            "business_name": "",
            "business_address": "",
            "contact_numbers": "",
            "search_resources": f"Error: {str(e)}",
        }

@app.get("/")
async def read_root():
    """Serve the main frontend page."""
    try:
        frontend_file = os.path.join(frontend_path, "index.html")
        if os.path.exists(frontend_file):
            return FileResponse(frontend_file)
        else:
            return JSONResponse(
                status_code=404, 
                content={"error": "Frontend files not found", "path": frontend_file}
            )
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": f"Server error: {str(e)}"}
        )

@app.post("/upload")
async def upload_csv(background_tasks: BackgroundTasks, file: UploadFile = File(...)):
    """Upload and process CSV file."""
    try:
        print(f"Received file: {file.filename}")
        
        if not file.filename.endswith('.csv'):
            raise HTTPException(status_code=400, detail="Only CSV files are allowed")
        
        # Read CSV content
        content = await file.read()
        print(f"File size: {len(content)} bytes")
        
        # Create temporary file
        with tempfile.NamedTemporaryFile(mode='wb', delete=False, suffix='.csv') as tmp_file:
            tmp_file.write(content)
            tmp_file_path = tmp_file.name
        
        # Read CSV with pandas
        try:
            df = pd.read_csv(tmp_file_path)
            print(f"CSV loaded successfully. Shape: {df.shape}")
            print(f"Columns: {list(df.columns)}")
        except Exception as e:
            os.unlink(tmp_file_path)
            raise HTTPException(status_code=400, detail=f"Error reading CSV: {str(e)}")
        
        # Clean up temp file
        os.unlink(tmp_file_path)
        
        # Validate required columns (flexible column names)
        required_cols = ["business_name", "Business_Name", "address", "Address"]
        if not any(col in df.columns for col in required_cols):
            available_cols = ", ".join(df.columns)
            raise HTTPException(
                status_code=400, 
                detail=f"CSV must contain either 'business_name'/'Business_Name' or 'address'/'Address' columns. Available columns: {available_cols}"
            )
        
        # Generate job ID
        job_id = str(uuid.uuid4())
        print(f"Generated job ID: {job_id}")
        
        # Start background processing
        background_tasks.add_task(process_csv_data, job_id, df)
        
        return {"job_id": job_id, "message": "File uploaded successfully, processing started"}
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Upload error: {e}")
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")

@app.get("/status/{job_id}")
async def get_job_status(job_id: str):
    """Get the status of a processing job."""
    if job_id not in job_status:
        raise HTTPException(status_code=404, detail="Job not found")
    
    return job_status[job_id]

@app.get("/results/{job_id}")
async def get_results(job_id: str):
    """Get the results of a completed job."""
    if job_id not in results_storage:
        raise HTTPException(status_code=404, detail="Results not found")
    
    return results_storage[job_id]["data"]

@app.get("/download/{job_id}")
async def download_results(job_id: str):
    """Download the results CSV file."""
    if job_id not in results_storage:
        raise HTTPException(status_code=404, detail="Results not found")
    
    file_path = results_storage[job_id]["path"]
    filename = results_storage[job_id]["filename"]
    
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")
    
    return FileResponse(
        path=file_path,
        filename=filename,
        media_type='application/octet-stream'
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 