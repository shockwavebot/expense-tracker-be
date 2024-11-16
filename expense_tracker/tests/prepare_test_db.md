# Test DB prep

```
docker exec -it expense_tracker_db psql -U postgres
CREATE DATABASE expense_tracker_test;

-- Create user if not exists
CREATE USER expense_tracker WITH PASSWORD 'expense_tracker_pass';

-- Grant privileges
GRANT ALL PRIVILEGES ON DATABASE expense_tracker_test TO expense_tracker;

-- Connect to the test database
\c expense_tracker_test

-- Grant schema privileges to the user
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO expense_tracker;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO expense_tracker;
GRANT ALL PRIVILEGES ON SCHEMA public TO expense_tracker;
ALTER USER expense_tracker WITH SUPERUSER;

```