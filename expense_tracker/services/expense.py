# expense_tracker/services/expense.py
from datetime import date
from typing import AsyncIterator, Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from expense_tracker.models.expense import Expense
from expense_tracker.models.user import User
from expense_tracker.schemas.expense import ExpenseCreate, ExpenseUpdate
from expense_tracker.services.base import BaseService


class ExpenseService(BaseService[Expense, ExpenseCreate, ExpenseUpdate]):
    """Service for handling expense-related operations"""

    def __init__(self, session: AsyncSession):
        super().__init__(Expense, session)

    async def create_expense(
        self, user: User, expense_data: ExpenseCreate
    ) -> Expense:
        """Create a new expense for a user"""
        expense = Expense(
            user_id=user.id,
            amount=expense_data.amount,
            description=expense_data.description,
            date=expense_data.date,
            category_id=expense_data.category_id,
        )
        self.session.add(expense)
        await self.session.commit()
        await self.session.refresh(expense)
        return expense

    async def get_user_expenses(
        self,
        user: User,
        skip: int = 0,
        limit: int = 100,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        category_id: Optional[UUID] = None,
    ) -> AsyncIterator[Expense]:
        """Get expenses for a specific user with optional filtering"""
        query = (
            select(Expense)
            .where(Expense.user_id == user.id)
            .offset(skip)
            .limit(limit)
            .order_by(Expense.date.desc())
        )

        # Apply filters if provided
        if start_date:
            query = query.where(Expense.date >= start_date)
        if end_date:
            query = query.where(Expense.date <= end_date)
        if category_id:
            query = query.where(Expense.category_id == category_id)

        result = await self.session.execute(query)
        for row in result.scalars():
            yield row

    async def get_expense(self, expense_id: UUID, user: User) -> Optional[Expense]:
        """Get a specific expense, ensuring it belongs to the user"""
        expense = await self.get(expense_id)
        if expense and expense.user_id == user.id:
            return expense
        return None

    async def update_expense(
        self, expense_id: UUID, user: User, expense_data: ExpenseUpdate
    ) -> Optional[Expense]:
        """Update an expense if it belongs to the user"""
        expense = await self.get_expense(expense_id, user)
        if not expense:
            return None

        # Update only provided fields
        update_data = expense_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(expense, field, value)

        await self.session.commit()
        await self.session.refresh(expense)
        return expense

    async def delete_expense(self, expense_id: UUID, user: User) -> bool:
        """Delete an expense if it belongs to the user"""
        expense = await self.get_expense(expense_id, user)
        if not expense:
            return False

        await self.session.delete(expense)
        await self.session.commit()
        return True
