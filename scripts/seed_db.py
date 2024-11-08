# scripts/seed_database.py
import asyncio
import datetime
import uuid
from datetime import date, timedelta
from decimal import Decimal
from typing import List

from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from expense_tracker.db.session import AsyncSessionLocal
from expense_tracker.models.category import Category
from expense_tracker.models.expense import Expense
from expense_tracker.models.shared_expense import SharedExpense, SharedExpenseStatus
from expense_tracker.models.user import User

current_time = datetime.datetime.now()


async def get_or_create_user(session: AsyncSession, email: str, username: str) -> User:
    """Get existing user or create a new one"""
    # Try to find existing user
    result = await session.execute(
        select(User).where(User.email == email)
    )
    user = result.scalar_one_or_none()

    if user:
        print(f"User {email} already exists")
        return user

    # Create new user
    user = User(
        email=email,
        username=username
    )
    session.add(user)
    try:
        await session.commit()
        print(f"Created new user: {email}")
    except IntegrityError:
        await session.rollback()
        # In case of race condition, try to fetch again
        result = await session.execute(
            select(User).where(User.email == email)
        )
        user = result.scalar_one()
        print(f"User {email} was created by another process")

    return user


async def get_or_create_category(
    session: AsyncSession,
    name: str,
    user_id: uuid.UUID = None
) -> Category:
    """Get existing category or create a new one"""
    # Try to find existing category
    query = select(Category).where(Category.name == name)
    if user_id:
        query = query.where(Category.user_id == user_id)
    else:
        query = query.where(Category.user_id.is_(None))

    result = await session.execute(query)
    category = result.scalar_one_or_none()

    if category:
        print(f"Category {name} already exists")
        return category

    # Create new category
    category = Category(
        name=name,
        user_id=user_id,
        created_at=current_time,
        updated_at=current_time
    )
    session.add(category)
    try:
        await session.commit()
        print(f"Created new category: {name}")
    except IntegrityError:
        await session.rollback()
        # In case of race condition, try to fetch again
        result = await session.execute(query)
        category = result.scalar_one()
        print(f"Category {name} was created by another process")

    return category


async def create_users(session: AsyncSession) -> List[User]:
    """Create test users if they don't exist"""
    users = []
    test_users = [
        ("john.doe@example.com", "John Doe"),
        ("jane.smith@example.com", "Jane Smith"),
        ("bob.wilson@example.com", "Bob Wilson")
    ]

    for email, username in test_users:
        user = await get_or_create_user(session, email, username)
        users.append(user)

    return users


async def create_categories(session: AsyncSession, users: List[User]) -> List[Category]:
    """Create both system and user-defined categories if they don't exist"""
    categories = []

    # System categories
    system_categories = [
        "Groceries",
        "Transportation",
        "Entertainment",
        "Healthcare",
        "Shopping",
        "Utilities",
        "Restaurants",
        "Travel"
    ]

    for name in system_categories:
        category = await get_or_create_category(session, name)
        categories.append(category)

    # User-defined categories
    user_categories = [
        (users[0], ["Weekend Fun", "Home Office"]),
        (users[1], ["Pet Supplies", "Hobbies"])
    ]

    for user, category_names in user_categories:
        for name in category_names:
            category = await get_or_create_category(session, name, user.id)
            categories.append(category)

    return categories


async def create_expense_if_not_exists(
    session: AsyncSession,
    user: User,
    category: Category,
    amount: Decimal,
    description: str,
    expense_date: date
) -> Expense:
    """Create an expense if it doesn't exist"""
    # Check for existing expense with same attributes
    result = await session.execute(
        select(Expense).where(
            Expense.user_id == user.id,
            Expense.category_id == category.id,
            Expense.amount == amount,
            Expense.description == description,
            Expense.date == expense_date
        )
    )
    expense = result.scalar_one_or_none()

    if expense:
        return expense

    expense = Expense(
        user_id=user.id,
        category_id=category.id,
        amount=amount,
        description=description,
        date=expense_date,
        created_at=current_time,
        updated_at=current_time
    )
    session.add(expense)
    await session.commit()
    return expense


async def create_expenses(
    session: AsyncSession,
    users: List[User],
    categories: List[Category]
) -> List[Expense]:
    """Create test expenses for each user if they don't exist"""
    expenses = []

    # Get category IDs by name for easier reference
    category_map = {cat.name: cat for cat in categories}

    # Create expenses for the last 3 months
    today = date.today()
    start_date = today - timedelta(days=90)

    # Sample expense data
    expense_templates = [
        ("Groceries", [50.00, 75.25, 120.50, 95.75]),
        ("Transportation", [25.00, 30.00, 45.50]),
        ("Entertainment", [80.00, 120.00, 65.50]),
        ("Restaurants", [35.50, 89.99, 42.25]),
        ("Shopping", [150.00, 200.00, 75.50]),
    ]

    for user in users:
        current_date = start_date
        while current_date <= today:
            # Add 1-3 expenses per day randomly
            for template in expense_templates:
                category_name, amounts = template
                # Only add some expenses some days
                if current_date.day % len(amounts) == 0:
                    expense = await create_expense_if_not_exists(
                        session,
                        user,
                        category_map[category_name],
                        Decimal(str(amounts[current_date.day % len(amounts)])),
                        f"{category_name} expense on {current_date}",
                        current_date
                    )
                    expenses.append(expense)
            current_date += timedelta(days=1)

    return expenses


async def create_shared_expense_if_not_exists(
    session: AsyncSession,
    expense: Expense,
    shared_with_user: User,
    split_percentage: Decimal
) -> SharedExpense:
    """Create a shared expense if it doesn't exist"""
    result = await session.execute(
        select(SharedExpense).where(
            SharedExpense.expense_id == expense.id,
            SharedExpense.shared_with_user_id == shared_with_user.id
        )
    )
    shared_expense = result.scalar_one_or_none()

    if shared_expense:
        return shared_expense

    shared_expense = SharedExpense(
        expense_id=expense.id,
        shared_with_user_id=shared_with_user.id,
        split_percentage=split_percentage,
        status=SharedExpenseStatus.PENDING,
        created_at=current_time,
        updated_at=current_time
    )
    session.add(shared_expense)
    await session.commit()
    return shared_expense


async def create_shared_expenses(
    session: AsyncSession,
    users: List[User],
    expenses: List[Expense]
) -> List[SharedExpense]:
    """Create shared expenses between users if they don't exist"""
    shared_expenses = []

    # Share every 5th expense with another user
    for i, expense in enumerate(expenses):
        if i % 5 == 0:
            # Find a user to share with (not the expense owner)
            share_with = next(
                user for user in users
                if user.id != expense.user_id
            )

            shared_expense = await create_shared_expense_if_not_exists(
                session,
                expense,
                share_with,
                Decimal("50.00")  # Split 50-50
            )
            shared_expenses.append(shared_expense)

    return shared_expenses


async def print_verification_data(session: AsyncSession):
    """Print sample data for verification"""
    # Get a sample user with their expenses
    user = (await session.execute(
        select(User)
        .filter(User.email == "john.doe@example.com")
        .options(selectinload(User.expenses))  # Eager load expenses
    )).scalar_one()

    print("\nSample user data:")
    print(f"Username: {user.username}")
    print(f"Email: {user.email}")

    # Count expenses safely
    expenses_count = await session.scalar(
        select(func.count())
        .select_from(Expense)
        .where(Expense.user_id == user.id)
    )
    print(f"Number of expenses: {expenses_count}")

    # Get some sample shared expenses
    shared = (await session.execute(
        select(SharedExpense)
        .options(
            selectinload(SharedExpense.expense),
            selectinload(SharedExpense.shared_with_user)
        )
        .limit(3)
    )).scalars().all()

    print("\nSample shared expenses:")
    for se in shared:
        print(
            f"Amount: ${se.expense.amount}, "
            f"Split: {se.split_percentage}%, "
            f"Shared with: {se.shared_with_user.username}, "
            f"Status: {se.status.value}"
        )


async def main():
    """Main function to seed the database"""
    print("Starting database seeding...⏳")

    async with AsyncSessionLocal() as session:
        # Create test data in order
        users = await create_users(session)
        categories = await create_categories(session, users)
        expenses = await create_expenses(session, users, categories)
        shared_expenses = await create_shared_expenses(session, users, expenses)

    print("Database seeding completed!✅")

    # Print verification data in a separate session
    async with AsyncSessionLocal() as session:
        await print_verification_data(session)

if __name__ == "__main__":
    asyncio.run(main())
