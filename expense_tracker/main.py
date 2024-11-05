# expense_tracker/main.py
from fastapi import FastAPI

from expense_tracker.api.v1.endpoints import auth, users
from expense_tracker.core.config import settings

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# Include routers
app.include_router(
    auth.router,
    prefix=f"{settings.API_V1_STR}/auth",
    tags=["authentication"]
)
app.include_router(
    users.router,
    prefix=f"{settings.API_V1_STR}/users",
    tags=["users"]
)


@app.get("/")
def read_root():
    return {"message": "Welcome to Expense Tracker API"}
