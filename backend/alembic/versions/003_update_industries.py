"""Update industries to detailed 2026-relevant list

Revision ID: 003
Revises: 002
Create Date: 2026-04-07
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "003"
down_revision: Union[str, None] = "002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

industries_table = sa.table(
    "industries",
    sa.column("name", sa.String),
    sa.column("slug", sa.String),
)

NEW_INDUSTRIES = [
    # Technology
    {"name": "AI / Machine Learning", "slug": "ai-ml"},
    {"name": "Data Science / Analytics", "slug": "data-science-analytics"},
    {"name": "Software Development (SDE)", "slug": "software-development"},
    {"name": "Cybersecurity", "slug": "cybersecurity"},
    {"name": "Cloud / DevOps / Infrastructure", "slug": "cloud-devops"},
    {"name": "Product Management (Tech)", "slug": "product-management-tech"},
    {"name": "IT Services / Tech Consulting", "slug": "it-services-consulting"},
    {"name": "Blockchain / Web3", "slug": "blockchain-web3"},
    # Finance
    {"name": "Investment Banking / Capital Markets", "slug": "investment-banking"},
    {"name": "Fintech", "slug": "fintech"},
    {"name": "Accounting / Audit / Tax (CA/ACCA)", "slug": "accounting-audit"},
    {"name": "Private Equity / Venture Capital", "slug": "pe-vc"},
    {"name": "Insurance / Risk Management", "slug": "insurance-risk"},
    # Consulting & Strategy
    {"name": "Management Consulting", "slug": "management-consulting"},
    {"name": "Strategy / Operations", "slug": "strategy-operations"},
    # Marketing & Media
    {"name": "Digital Marketing / Growth", "slug": "digital-marketing"},
    {"name": "Advertising / Brand Management", "slug": "advertising-brand"},
    {"name": "Media / Content / Journalism", "slug": "media-content"},
    {"name": "Public Relations / Communications", "slug": "pr-communications"},
    # Design & Creative
    {"name": "UI/UX Design", "slug": "ui-ux-design"},
    {"name": "Product Design", "slug": "product-design"},
    {"name": "Graphic Design / Visual Arts", "slug": "graphic-design"},
    # Healthcare & Sciences
    {"name": "Healthcare / Pharma", "slug": "healthcare-pharma"},
    {"name": "Biotech / Life Sciences", "slug": "biotech-life-sciences"},
    # Law & Policy
    {"name": "Legal / Compliance", "slug": "legal-compliance"},
    {"name": "Public Policy / Government", "slug": "public-policy-govt"},
    # Engineering (Non-Software)
    {"name": "Mechanical / Civil / Electrical Engineering", "slug": "core-engineering"},
    {"name": "Manufacturing / Operations", "slug": "manufacturing-operations"},
    # Business & Commerce
    {"name": "E-Commerce / Retail", "slug": "ecommerce-retail"},
    {"name": "Supply Chain / Logistics", "slug": "supply-chain-logistics"},
    {"name": "Real Estate / PropTech", "slug": "real-estate-proptech"},
    {"name": "Human Resources / People Ops", "slug": "human-resources"},
    # Emerging & Other
    {"name": "EdTech / Education", "slug": "edtech-education"},
    {"name": "Sustainability / CleanTech", "slug": "sustainability-cleantech"},
    {"name": "Entrepreneurship / Startups", "slug": "entrepreneurship"},
    {"name": "Other", "slug": "other"},
]


def upgrade() -> None:
    op.execute("DELETE FROM submissions")
    op.execute("DELETE FROM industries")
    op.bulk_insert(industries_table, NEW_INDUSTRIES)


def downgrade() -> None:
    op.execute("DELETE FROM industries")
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
