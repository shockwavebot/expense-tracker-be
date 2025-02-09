"""Add missing constraints

Revision ID: 1ec723a7a736
Revises: f9b3a9506e85
Create Date: 2024-11-07 20:35:20.789498

"""
from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = '1ec723a7a736'
down_revision: Union[str, None] = 'f9b3a9506e85'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create users table
    op.create_table(
        'user',
        sa.Column('id', sa.UUID(as_uuid=True), primary_key=True),
        sa.Column('email', sa.String(255), nullable=False, unique=True),
        sa.Column('username', sa.String(100), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False)
    )

    # Create categories table
    op.create_table(
        'category',
        sa.Column('id', sa.UUID(as_uuid=True), primary_key=True),
        sa.Column('name', sa.String(50), nullable=False),
        sa.Column('user_id', sa.UUID(as_uuid=True), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['user.id'], ondelete='CASCADE')
    )

    # Create expenses table
    op.create_table(
        'expense',
        sa.Column('id', sa.UUID(as_uuid=True), primary_key=True),
        sa.Column('amount', sa.Numeric(10, 2), nullable=False),
        sa.Column('description', sa.String(255), nullable=False),
        sa.Column('date', sa.Date(), nullable=False),
        sa.Column('user_id', sa.UUID(as_uuid=True), nullable=False),
        sa.Column('category_id', sa.UUID(
            as_uuid=True), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['user.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(
            ['category_id'], ['category.id'], ondelete='RESTRICT')
    )

    # Create shared_expense table
    op.create_table(
        'shared_expense',
        sa.Column('id', sa.UUID(as_uuid=True), primary_key=True),
        sa.Column('expense_id', sa.UUID(as_uuid=True), nullable=False),
        sa.Column('shared_with_user_id', sa.UUID(
            as_uuid=True), nullable=False),
        sa.Column('split_percentage', sa.Numeric(5, 2), nullable=False),
        sa.Column('status', sa.Enum('PENDING', 'ACCEPTED', 'REJECTED',
                  'SETTLED', name='sharedexpensestatus'), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(
            ['expense_id'], ['expense.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['shared_with_user_id'], [
                                'user.id'], ondelete='CASCADE')
    )


def downgrade() -> None:
    op.drop_table('shared_expense')
    op.drop_table('expense')
    op.drop_table('category')
    op.drop_table('user')
    op.execute('DROP TYPE sharedexpensestatus')
