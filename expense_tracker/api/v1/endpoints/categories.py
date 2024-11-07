from typing import Annotated, List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from expense_tracker.core.security import get_current_user
from expense_tracker.db.session import get_session
from expense_tracker.models.category import Category
from expense_tracker.models.user import User
from expense_tracker.schemas.category import Category as CategorySchema
from expense_tracker.schemas.category import CategoryCreate, CategoryUpdate

router = APIRouter()


@router.post("", response_model=CategorySchema, status_code=status.HTTP_201_CREATED)
async def create_category(
    category_in: CategoryCreate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_session)]
):
    """
    Create new category for the current user.
    """
    # Check if category with this name already exists for the user
    result = await db.execute(
        select(Category).where(
            Category.user_id == current_user.id,
            Category.name == category_in.name
        )
    )
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Category with this name already exists"
        )

    category = Category(
        name=category_in.name,
        description=category_in.description,
        user_id=current_user.id
    )
    db.add(category)
    await db.commit()
    await db.refresh(category)
    return category


@router.get("", response_model=List[CategorySchema])
async def read_categories(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_session)],
    skip: int = 0,
    limit: int = 100
):
    """
    Retrieve categories for the current user.
    """
    result = await db.execute(
        select(Category)
        .where(Category.user_id == current_user.id)
        .offset(skip)
        .limit(limit)
    )
    return result.scalars().all()


@router.get("/{category_id}", response_model=CategorySchema)
async def read_category(
    category_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_session)]
):
    """
    Get a specific category by ID.
    """
    result = await db.execute(
        select(Category).where(
            Category.id == category_id,
            Category.user_id == current_user.id
        )
    )
    category = result.scalar_one_or_none()
    if category is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found"
        )
    return category


@router.put("/{category_id}", response_model=CategorySchema)
async def update_category(
    category_id: int,
    category_in: CategoryUpdate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_session)]
):
    """
    Update a category.
    """
    result = await db.execute(
        select(Category).where(
            Category.id == category_id,
            Category.user_id == current_user.id
        )
    )
    category = result.scalar_one_or_none()
    if category is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found"
        )

    # Check if new name conflicts with existing category
    if category_in.name and category_in.name != category.name:
        name_check = await db.execute(
            select(Category).where(
                Category.user_id == current_user.id,
                Category.name == category_in.name,
                Category.id != category_id
            )
        )
        if name_check.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Category with this name already exists"
            )

    # Update category attributes
    update_data = category_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(category, field, value)

    db.add(category)
    await db.commit()
    await db.refresh(category)
    return category


@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_category(
    category_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_session)]
):
    """
    Delete a category.
    """
    result = await db.execute(
        select(Category).where(
            Category.id == category_id,
            Category.user_id == current_user.id
        )
    )
    category = result.scalar_one_or_none()
    if category is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found"
        )

    await db.delete(category)
    await db.commit()
