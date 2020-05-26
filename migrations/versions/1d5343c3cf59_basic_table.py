"""basic table

Revision ID: 1d5343c3cf59
Revises: 
Create Date: 2020-01-05 08:56:46.540294

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '1d5343c3cf59'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('basics',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('author_id', sa.Integer(), nullable=True),
    sa.Column('height', sa.Integer(), nullable=True),
    sa.Column('weight', sa.Float(precision=2), nullable=True),
    sa.Column('sit_up', sa.Integer(), nullable=True),
    sa.Column('pull_up', sa.Integer(), nullable=True),
    sa.Column('long_run', sa.Float(precision=2), nullable=True),
    sa.Column('retrace', sa.Float(precision=2), nullable=True),
    sa.Column('timestamp', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['author_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_basics_timestamp'), 'basics', ['timestamp'], unique=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_basics_timestamp'), table_name='basics')
    op.drop_table('basics')
    # ### end Alembic commands ###
