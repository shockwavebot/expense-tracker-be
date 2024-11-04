# Expense Tracker 

App for logging personal expenses 


## Usage 

Setup Python virtual env with uv: `uv sync`

Start PostgreSQL `docker-compose up -d`

Start the FastAPI application with uvicorn `uvicorn expense_tracker.main:app --reload --workers 1`

### DB migration

Initialize alembic `alembic init alembic`

Create initial migration
`alembic revision --autogenerate -m "Create users and categories tables"`

Run the migration
`alembic upgrade head`