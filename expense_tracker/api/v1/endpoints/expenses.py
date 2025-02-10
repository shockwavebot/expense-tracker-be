# expense_tracker/api/v1/endpoints/expenses.py
from datetime import date
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from expense_tracker.db.session import get_session
from expense_tracker.models.user import User
from expense_tracker.schemas.expense import (ExpenseCreate, ExpenseResponse,
                                             ExpenseUpdate)
from expense_tracker.services.expense import ExpenseService
from expense_tracker.services.user import get_current_user

router = APIRouter(prefix="/expenses", tags=["expenses"])


@router.post("", response_model=ExpenseResponse)
async def create_expense(
    expense_data: ExpenseCreate,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    """Create a new expense"""
    expense_service = ExpenseService(session)
    expense = await expense_service.create_expense(current_user, expense_data)
    return expense


@router.get("", response_model=List[ExpenseResponse])
async def list_expenses(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    category_id: Optional[UUID] = None,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    """List user's expenses with optional filtering"""
    expense_service = ExpenseService(session)
    expenses = [
        expense
        async for expense in expense_service.get_user_expenses(
            current_user,
            skip=skip,
            limit=limit,
            start_date=start_date,
            end_date=end_date,
            category_id=category_id,
        )
    ]
    return expenses


@router.get("/{expense_id}", response_model=ExpenseResponse)
async def get_expense(
    expense_id: UUID,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    """Get a specific expense"""
    expense_service = ExpenseService(session)
    expense = await expense_service.get_expense(expense_id, current_user)
    if not expense:
        raise HTTPException(status_code=404, detail="Expense not found")
    return expense


@router.put("/{expense_id}", response_model=ExpenseResponse)
async def update_expense(
    expense_id: UUID,
    expense_data: ExpenseUpdate,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    """Update an expense"""
    expense_service = ExpenseService(session)
    expense = await expense_service.update_expense(
        expense_id, current_user, expense_data
    )
    if not expense:
        raise HTTPException(status_code=404, detail="Expense not found")
    return expense


@router.delete("/{expense_id}", status_code=204)
async def delete_expense(
    expense_id: UUID,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    """Delete an expense"""
    expense_service = ExpenseService(session)
    deleted = await expense_service.delete_expense(expense_id, current_user)
    if not deleted:
        raise HTTPException(status_code=404, detail="Expense not found")
    deleted = await expense_service.delete_expense(expense_id, current_user)
    if not deleted:
        raise HTTPException(status_code=404, detail="Expense not found")
