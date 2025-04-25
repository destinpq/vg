"""create activity logs table

Revision ID: 37a24f31e5a9
Revises: 
Create Date: 2023-04-20 19:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '37a24f31e5a9'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Create activity_logs table
    op.create_table(
        'activity_logs',
        sa.Column('id', sa.String(64), primary_key=True, index=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('endpoint', sa.String(256), nullable=False),
        sa.Column('method', sa.String(16), nullable=False),
        sa.Column('path', sa.String(256), nullable=False),
        sa.Column('ip_address', sa.String(45), nullable=True),
        sa.Column('user_id', sa.String(64), nullable=True, index=True),
        sa.Column('request_data', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('response_data', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('start_time', sa.DateTime(), nullable=False),
        sa.Column('end_time', sa.DateTime(), nullable=True),
        sa.Column('duration_ms', sa.Float(), nullable=True),
        sa.Column('status_code', sa.Integer(), nullable=True),
        sa.Column('success', sa.Boolean(), nullable=True),
        sa.Column('error', sa.Text(), nullable=True),
        sa.Column('metadata', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
    )
    
    # Create indices for faster queries
    op.create_index('ix_activity_logs_created_at', 'activity_logs', ['created_at'])
    op.create_index('ix_activity_logs_endpoint', 'activity_logs', ['endpoint'])
    op.create_index('ix_activity_logs_method', 'activity_logs', ['method'])
    op.create_index('ix_activity_logs_status_code', 'activity_logs', ['status_code'])
    op.create_index('ix_activity_logs_success', 'activity_logs', ['success'])


def downgrade():
    # Drop indices first
    op.drop_index('ix_activity_logs_success', table_name='activity_logs')
    op.drop_index('ix_activity_logs_status_code', table_name='activity_logs')
    op.drop_index('ix_activity_logs_method', table_name='activity_logs')
    op.drop_index('ix_activity_logs_endpoint', table_name='activity_logs')
    op.drop_index('ix_activity_logs_created_at', table_name='activity_logs')
    
    # Drop table
    op.drop_table('activity_logs') 