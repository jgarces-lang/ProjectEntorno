"""create tienda tables (categorias, productos, admins)

Revision ID: 0001
Revises:
Create Date: 2026-06-07
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "admins",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("username", sa.String(), nullable=False),
        sa.Column("password_hash", sa.String(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_admins_username"), "admins", ["username"], unique=True)

    op.create_table(
        "categorias",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("nombre", sa.String(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_categorias_nombre"), "categorias", ["nombre"], unique=True)

    op.create_table(
        "productos",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("nombre", sa.String(), nullable=False),
        sa.Column("precio", sa.Float(), nullable=False),
        sa.Column("descripcion", sa.String(), nullable=False),
        sa.Column("categoria_id", sa.Integer(), nullable=True),
        sa.Column("imagen_url", sa.String(), nullable=False),
        sa.Column("activo", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["categoria_id"], ["categorias.id"], ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_productos_nombre"), "productos", ["nombre"])


def downgrade() -> None:
    op.drop_index(op.f("ix_productos_nombre"), table_name="productos")
    op.drop_table("productos")
    op.drop_index(op.f("ix_categorias_nombre"), table_name="categorias")
    op.drop_table("categorias")
    op.drop_index(op.f("ix_admins_username"), table_name="admins")
    op.drop_table("admins")
