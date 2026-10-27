from typing import Literal

from pydantic import BaseModel, Field

from cike_nexus.data.enums.ToolType import ToolType


class SkillToolConfigValue(BaseModel):
    type: Literal[ToolType.SKILL] = Field(
        default=ToolType.SKILL, description="类型标识，固定为 SKILL"
    )
    url: str = Field(description="Skill 资源地址")
