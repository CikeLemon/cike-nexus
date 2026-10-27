from sqlalchemy import BigInteger
from sqlmodel import Field

from cike_nexus.data.abstracts.FullAuditedEntity import AuditedEntity


class AgentConversationMessage(AuditedEntity, table=True):
    conversation_id: int = Field(description="会话id")
    contents: str = Field(description="内容,json数组")
    duration_seconds: int = Field(description="耗时", default=0, sa_type=BigInteger)
    role:str =Field(description="角色 user|ai",)
