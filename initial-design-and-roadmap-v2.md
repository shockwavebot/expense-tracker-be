# Expense Tracker Application Design Document

## 1. System Architecture

### Database Schema
```
Users
- id: UUID (primary key)
- email: String (unique)
- name: String
- created_at: Timestamp
- updated_at: Timestamp

Expenses
- id: UUID (primary key)
- user_id: UUID (foreign key)
- amount: Decimal
- description: String
- category: String
- date: Date
- created_at: Timestamp
- updated_at: Timestamp

SharedExpenses
- id: UUID (primary key)
- expense_id: UUID (foreign key)
- shared_with_user_id: UUID (foreign key)
- split_percentage: Decimal
- status: Enum (PENDING, ACCEPTED, REJECTED, SETTLED)
- created_at: Timestamp
- updated_at: Timestamp

Categories
- id: UUID (primary key)
- name: String
- user_id: UUID (foreign key, null for system categories)
- created_at: Timestamp
- updated_at: Timestamp
```

### API Endpoints

#### User Management
- POST /api/v1/users - Register new user
- GET /api/v1/users/me - Get current user
- PUT /api/v1/users/me - Update user profile

#### Expense Management
- POST /api/v1/expenses - Create new expense
- GET /api/v1/expenses - List expenses (with filtering)
- GET /api/v1/expenses/{id} - Get specific expense
- PUT /api/v1/expenses/{id} - Update expense
- DELETE /api/v1/expenses/{id} - Delete expense

#### Shared Expenses
- POST /api/v1/expenses/{id}/share - Share expense with users
- GET /api/v1/shared-expenses - List shared expenses
- PUT /api/v1/shared-expenses/{id}/status - Update shared expense status

#### Categories
- GET /api/v1/categories - List categories
- POST /api/v1/categories - Create custom category
- PUT /api/v1/categories/{id} - Update category
- DELETE /api/v1/categories/{id} - Delete category

#### Analytics
- GET /api/v1/analytics/expenses/by-category - Get expenses grouped by category
- GET /api/v1/analytics/expenses/by-date - Get expenses grouped by date range
- GET /api/v1/analytics/trends - Get spending trends

## 2. Development Roadmap

### Phase 1: Project Setup and Core Infrastructure
1. Initialize project structure
2. Set up Docker environment
3. Configure PostgreSQL
4. Implement database migrations
5. Set up FastAPI application structure
6. Configure dependency injection
7. Implement error handling

### Phase 2: Core Features Implementation
1. User management
2. Basic expense CRUD operations
3. Category management
4. Basic filtering and querying

### Phase 3: Shared Expenses Feature
1. Implement expense sharing logic
2. Add notification system for shared expenses
3. Implement settlement tracking

### Phase 4: Analytics and Reporting
1. Implement expense aggregation
2. Add date-based filtering
3. Create trend analysis
4. Export functionality

### Phase 5: Testing and Documentation
1. Unit tests
2. Integration tests
3. API documentation
4. User documentation

## 3. Implementation Details

### Technology Stack Details
- FastAPI for REST API
- SQLAlchemy for ORM
- Alembic for migrations
- Pydantic for data validation
- PostgreSQL for database
- Docker for containerization
- UV for dependency management

### Best Practices
1. Use dependency injection
2. Implement proper error handling
3. Follow REST API conventions
4. Use async/await where appropriate
5. Implement proper validation
6. Use type hints
7. Follow PEP 8 style guide