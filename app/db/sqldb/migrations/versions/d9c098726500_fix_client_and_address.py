"""Fix client and address
Revision ID: d9c098726500
Revises: c0bcb03c2e93
Create Date: 2023-08-02 10:16:08.552784
"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic
revision = 'd9c098726500'
down_revision = 'c0bcb03c2e93'
branch_labels = None
depends_on = None

def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint('client_fk_address', 'client', type_='foreignkey')
    op.drop_column('client', 'address_id')
    # ### end Alembic commands ###

def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('client', sa.Column('address_id', sa.INTEGER(), autoincrement=False, nullable=False))
    op.create_foreign_key('client_fk_address', 'client', 'address', ['address_id'], ['id'], ondelete='CASCADE')
    # ### end Alembic commands ###
