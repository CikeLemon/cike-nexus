from sqlalchemy import BigInteger
from sqlmodel import Field

from cike_nexus.data.abstracts.FullAuditedEntity import FullAuditedEntity,AuditedEntity


class AgentConversationMessageContent(AuditedEntity, table=True):
    conversation_id: int = Field(description="会话id",sa_type=BigInteger)
    conversation_message_id:int = Field(description="会话消息id",sa_type=BigInteger)
    content_type:str= Field(description="内容类型")
    content: str = Field(description="内容,字符串|json对象")
    duration_seconds: int = Field(description="耗时", default=0, sa_type=BigInteger)
