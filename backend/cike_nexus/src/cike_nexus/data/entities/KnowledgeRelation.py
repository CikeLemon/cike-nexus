from sqlmodel import Field

from cike_nexus.data.abstracts.FullAuditedEntity import FullAuditedEntity
from sqlalchemy import BigInteger


class KnowledgeRelation(FullAuditedEntity, table=True):
    knowledge_id: int = Field(default="知识库id", index=True, nullable=False, sa_type=BigInteger)
    correlation_id: int = Field(description="关联id", index=True, nullable=False, sa_type=BigInteger)
    correlation_type:int = Field(description="关联类型：1：agent，2：department")
