"""将工具配置改为非空，不自动填充存量配置。"""

from typing import Sequence

from alembic import context, op
import sqlalchemy as sa


revision: str = "fa0e32874b19"
down_revision: str | Sequence[str] | None = "c6510b57d8b4"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """先拒绝存量空配置，再收紧列的空值约束。"""
    # 离线输出无法读取存量数据；实际升级应在线运行以执行这项检查。
    if not context.is_offline_mode():
        empty_config = op.get_bind().execute(
            sa.text(
                "SELECT 1 FROM tool "
                "WHERE config IS NULL OR JSON_TYPE(config) = 'NULL' LIMIT 1"
            )
        ).first()
        if empty_config is not None:
            raise RuntimeError("存在空的工具配置，请先补齐或处理数据后再执行迁移")

    op.alter_column(
        "tool",
        "config",
        existing_type=sa.JSON(),
        existing_nullable=True,
        nullable=False,
    )


def downgrade() -> None:
    """恢复可空约束，不修改已有配置内容。"""
    op.alter_column(
        "tool",
        "config",
        existing_type=sa.JSON(),
        existing_nullable=False,
        nullable=True,
    )
