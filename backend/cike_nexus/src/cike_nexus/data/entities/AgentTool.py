from sqlmodel import Field

from cike_nexus.data.abstracts.FullAuditedEntity import FullAuditedEntity
from sqlalchemy import BigInteger


class AgentTool(FullAuditedEntity, table=True):
    agent_id: int = Field(description="AgentId", index=True, nullable=False, sa_type=BigInteger)
    tool_id: int = Field(default="工具id", index=True, nullable=False, sa_type=BigInteger)
