from sqlalchemy import BigInteger
from sqlmodel import Field

from cike_nexus.data.abstracts.FullAuditedEntity import FullAuditedEntity


class AgentConversation(FullAuditedEntity, table=True):
    name: str = Field(description="名称", index=True, nullable=False, max_length=256)
    description: str = Field(default="描述", nullable=False, max_length=512)
    agent_id:int = Field(default=0, nullable=False, index=True, sa_type=BigInteger)