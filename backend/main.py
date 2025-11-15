from fastapi import FastAPI
from routers import tryon, furniture, room_designs, furniture_placement
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Allow frontend to connect
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # or ["http://localhost:3000"] for React
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(tryon.router, prefix="/api")
app.include_router(furniture.router, prefix="/api")
app.include_router(room_designs.router, prefix="/api")
app.include_router(furniture_placement.router, prefix="/api")
