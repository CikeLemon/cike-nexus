from sqlmodel import Field

from cike_nexus.data.abstracts.FullAuditedEntity import FullAuditedEntity
from sqlalchemy import BigInteger


class DepartmentUser(FullAuditedEntity, table=True):
    department_id: int = Field(description="部门id", index=True, nullable=False, sa_type=BigInteger)
    user_id: int = Field(default="用户id", index=True, nullable=False, sa_type=BigInteger)
