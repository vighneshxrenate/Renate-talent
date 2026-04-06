"""Seed colleges and industries

Revision ID: 002
Revises: 001
Create Date: 2026-04-07
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "002"
down_revision: Union[str, None] = "001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

colleges_table = sa.table(
    "colleges",
    sa.column("name", sa.String),
    sa.column("slug", sa.String),
)

industries_table = sa.table(
    "industries",
    sa.column("name", sa.String),
    sa.column("slug", sa.String),
)


def upgrade() -> None:
    op.bulk_insert(
        colleges_table,
        [
            {"name": "Atlas SkillTech University", "slug": "atlas"},
            {"name": "NMIMS University", "slug": "nmims"},
            {"name": "DY Patil University", "slug": "dy-patil"},
            {"name": "IIT Bombay", "slug": "iit-bombay"},
        ],
    )

    op.bulk_insert(
        industries_table,
        [
            {"name": "IT / Software", "slug": "it-software"},
            {"name": "Finance / Accounting", "slug": "finance-accounting"},
            {"name": "Consulting", "slug": "consulting"},
            {"name": "Marketing / Advertising", "slug": "marketing-advertising"},
            {"name": "Healthcare / Pharma", "slug": "healthcare-pharma"},
            {"name": "Legal", "slug": "legal"},
            {"name": "Media / Entertainment", "slug": "media-entertainment"},
            {"name": "Education", "slug": "education"},
            {"name": "Manufacturing / Engineering", "slug": "manufacturing-engineering"},
            {"name": "Real Estate / Construction", "slug": "real-estate-construction"},
            {"name": "E-Commerce / Retail", "slug": "ecommerce-retail"},
            {"name": "Other", "slug": "other"},
        ],
    )


def downgrade() -> None:
    op.execute("DELETE FROM industries")
    op.execute("DELETE FROM colleges")
