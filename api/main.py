import os
from dotenv import load_dotenv
from fastapi import FastAPI 
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from logging_config import get_logger
from router import router

logger = get_logger(__name__)

load_dotenv()

app = FastAPI(
    title="Local Content Generator API",
    version="0.1.0",
    debug=True
)

# Allow all origins (not safe for production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # domains allowed to access the API
    allow_credentials=True,
    allow_methods=["*"],   # HTTP methods allowed (GET, POST, etc.)
    allow_headers=["*"],   # headers allowed in requests
)

app.include_router(router)

# Create output directory if it doesn't exist
output_dir = "output"
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

# Mount the output directory as a static files directory
app.mount("/output", StaticFiles(directory=output_dir), name="output")
