from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
import uvicorn
import os

app = FastAPI(title="Hackathon MVP — Template")

# Enable CORS for frontend development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount the frontend directory to serve CSS/JS/Images
# Note: Ensure the 'frontend' folder exists in the project root
frontend_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend")
app.mount("/static", StaticFiles(directory=frontend_path), name="static")

@app.get("/")
async def read_index():
    return FileResponse(os.path.join(frontend_path, "index.html"))

@app.get("/api/health")
async def health_check():
    return {"status": "ok", "message": "API is online"}

if __name__ == "__main__":
    # This allows us to run the app from the root directory easily
    import sys
    sys.path.append(os.path.dirname(os.path.dirname(__file__)))
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
