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

```
➜ alembic revision --autogenerate -m "Initial migration"
INFO  [alembic.runtime.migration] Context impl PostgresqlImpl.
INFO  [alembic.runtime.migration] Will assume transactional DDL.
  Generating /Users/markostanojlovic/code/expense-tracker/alembic/versions/a2e70ed5ecaa_initial_migration.py ...  done

➜ alembic upgrade head
INFO  [alembic.runtime.migration] Context impl PostgresqlImpl.
INFO  [alembic.runtime.migration] Will assume transactional DDL.
INFO  [alembic.runtime.migration] Running upgrade  -> a2e70ed5ecaa, Initial migration
```


```
docker exec -it expense_tracker_db psql -U postgres -d expense_tracker -c "\dt"

              List of relations
 Schema |      Name       | Type  |  Owner
--------+-----------------+-------+----------
 public | alembic_version | table | postgres
 public | categories      | table | postgres
 public | users           | table | postgres
```

```
curl -X POST "http://localhost:8000/api/v1/users" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "password123",
    "username": "testuser"
  }'
```