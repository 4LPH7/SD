from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from services.propagation_service import get_current_debris_positions

app = FastAPI()

# Configure CORS
origins = [
    "http://localhost:8080",  # Allow the frontend development server
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"status": "Orbital Debris API is running"}

@app.get("/api/debris/positions")
async def get_debris_positions():
    """
    API endpoint to get the current calculated positions of all debris.
    """
    positions = get_current_debris_positions()
    return positions