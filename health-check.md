# Health check
## Start db&app 
TODO: one command to rule them all

```
docker-compose up -d
uvicorn expense_tracker.main:app --reload --workers 1

```

Example: 
```
➜ docker-compose up -d
[+] Running 2/2
 ✔ Network expense-tracker_expense_tracker_network  Created   0.0s
 ✔ Container expense_tracker_db  Started                      0.2s

➜ docker-compose up -d
[+] Running 1/0
 ✔ Container expense_tracker_db  Running                       0.0s

➜ uvicorn expense_tracker.main:app --reload --workers 1
INFO:     Will watch for changes in these directories: ['/Users/markostanojlovic/code/expense-tracker']
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [65712] using StatReload
INFO:     Started server process [65714]
INFO:     Waiting for application startup.
INFO:     Application startup complete.

```

## Test all endpoints 
### Requirements
#### Clone prod db for testing purposes 
`CREATE DATABASE expense_tracker_test TEMPLATE expense_tracker;`
### Run endpoint tests 
While db and app are running:
`pytest test/ -v`

```
➜ pytest test/ -v

================================================================ test session starts =================================================================
platform darwin -- Python 3.12.7, pytest-8.3.3, pluggy-1.5.0 -- /Users/markostanojlovic/code/expense-tracker/.venv/bin/python3
cachedir: .pytest_cache
rootdir: /Users/markostanojlovic/code/expense-tracker
configfile: pyproject.toml
plugins: asyncio-0.24.0, cov-6.0.0, env-1.1.5, anyio-4.6.2.post1
asyncio: mode=Mode.STRICT, default_loop_scope=function
collected 5 items

test/test_users.py::TestUserEndpoints::test_create_user PASSED                                                                                 [ 20%]
test/test_users.py::TestUserEndpoints::test_get_user PASSED                                                                                    [ 40%]
test/test_users.py::TestUserEndpoints::test_update_user PASSED                                                                                 [ 60%]
test/test_users.py::TestUserEndpoints::test_delete_user PASSED                                                                                 [ 80%]
test/test_users.py::TestUserEndpoints::test_list_users PASSED                                                                                  [100%]

================================================================= 5 passed in 0.21s ==================================================================

```


