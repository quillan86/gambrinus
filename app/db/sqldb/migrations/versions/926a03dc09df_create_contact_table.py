"""create contact table
Revision ID: 926a03dc09df
Revises: fde8532aa464
Create Date: 2023-09-21 14:54:26.626466
"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic
revision = '926a03dc09df'
down_revision = 'fde8532aa464'
branch_labels = None
depends_on = None

def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('contact',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=200), nullable=False),
    sa.Column('email', sa.String(length=200), nullable=False),
    sa.Column('message', sa.UnicodeText(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###

def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('contact')
    # ### end Alembic commands ###