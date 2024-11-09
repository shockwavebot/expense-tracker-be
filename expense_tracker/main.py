# expense_tracker/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from expense_tracker.api.v1.endpoints import users
from expense_tracker.core.settings import settings

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="API for tracking personal and shared expenses",
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# CORS middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Modify this in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(
    users.router,
    prefix=f"{settings.API_V1_STR}/users",
    tags=["users"]
)


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


@app.get("/")
def read_root():
    return {"message": "Welcome to Expense Tracker API"}
