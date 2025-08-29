from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.models import Base, engine
from app.api import cases_router, advisors_router, assignments_router
from app.api.excel_upload import router as excel_upload_router
from app.startup import initialize_database
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Create database tables
Base.metadata.create_all(bind=engine)

# Initialize database with sample data if empty
initialize_database()

app = FastAPI(
    title="AdvisorConnect GenAI v2",
    description="AI-powered advisor matching system",
    version="2.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(cases_router)
app.include_router(advisors_router)
app.include_router(assignments_router)
app.include_router(excel_upload_router)

@app.get("/")
async def root():
    return {
        "message": "AdvisorConnectAPI",
        "version": "2.0.0",
        "docs": "/docs"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
