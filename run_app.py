#!/usr/bin/env python3
"""
ARM Skip Trace Application Launcher
Convenient script to start the web application
"""

import os
import sys
import subprocess
import webbrowser
import time
from pathlib import Path

def check_file_structure():
    """Check if all required files exist."""
    required_files = [
        "backend/main.py",
        "frontend/index.html",
        "frontend/style.css", 
        "frontend/script.js",
        "WebSearchLLM.py",
        "requirements.txt"
    ]
    
    missing_files = []
    for file_path in required_files:
        if not Path(file_path).exists():
            missing_files.append(file_path)
    
    if missing_files:
        print("❌ Missing required files:")
        for file in missing_files:
            print(f"   - {file}")
        return False
    
    print("✅ All required files found.")
    return True

def check_requirements():
    """Check if all required packages are installed."""
    try:
        import fastapi
        import uvicorn
        import pandas
        import openai
        from dotenv import load_dotenv
        print("✅ All required packages are installed.")
        return True
    except ImportError as e:
        print(f"❌ Missing required package: {e}")
        print("Please run: pip install -r requirements.txt")
        return False

def check_env_file():
    """Check if .env file exists and has OpenAI API key."""
    env_path = Path(".env")
    if not env_path.exists():
        print("❌ .env file not found!")
        print("Please create a .env file with your OpenAI API key:")
        print("OPENAI_API_KEY=your_api_key_here")
        return False
    
    # Check if the file contains an API key
    content = env_path.read_text()
    if "OPENAI_API_KEY" not in content or "your_openai_api_key_here" in content:
        print("⚠️  Please make sure to set your actual OpenAI API key in the .env file")
        print("Current .env file needs a valid OPENAI_API_KEY")
        return False
    
    print("✅ .env file found with API key.")
    return True

def start_server():
    """Start the FastAPI server."""
    print("🚀 Starting ARM Skip Trace server...")
    print("📍 Server will be available at: http://localhost:8000")
    print("🔧 Use Ctrl+C to stop the server")
    print("-" * 50)
    
    try:
        # Change to the correct directory structure
        cmd = [
            sys.executable, 
            "-m", "uvicorn", 
            "backend.main:app", 
            "--host", "0.0.0.0", 
            "--port", "8000",
            "--reload"
        ]
        
        # Start the server
        process = subprocess.Popen(cmd)
        
        # Wait a moment for server to start, then open browser
        print("⏳ Waiting for server to start...")
        time.sleep(3)
        print("🌐 Opening web browser...")
        webbrowser.open("http://localhost:8000")
        
        # Wait for the process to complete
        process.wait()
        
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user.")
        if 'process' in locals():
            process.terminate()
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        print("Try running manually: uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload")

def main():
    """Main function to run all checks and start the application."""
    print("=" * 60)
    print("🔍 ARM Skip Trace - Business Contact Finder")
    print("=" * 60)
    print()
    
    # Run all checks
    if not check_file_structure():
        print("\n💡 Make sure you're running this from the project root directory")
        sys.exit(1)
    
    if not check_requirements():
        sys.exit(1)
    
    if not check_env_file():
        sys.exit(1)
    
    print("🎯 All checks passed! Starting application...")
    print()
    
    start_server()

if __name__ == "__main__":
    main() 