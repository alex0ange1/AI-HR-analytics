"""'professions'

Revision ID: 475998c5f82d
Revises: 36ca45806a74
Create Date: 2025-04-11 14:32:14.995265

"""
from alembic import op
import sqlalchemy as sa

from project.core.config import settings
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '475998c5f82d'
down_revision = '36ca45806a74'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('professions',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String().with_variant(sa.String(length=255), 'postgresql'), nullable=False),
    sa.Column('competencies', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('name'),
    schema='schema_competency'
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('professions', schema='schema_competency')
    # ### end Alembic commands ###