from typing import Annotated, Union

from pydantic import BeforeValidator
from sqlalchemy import JSON
from sqlmodel import Field, Column

from cike_nexus.data.abstracts.FullAuditedEntity import FullAuditedEntity
from cike_nexus.data.enums.ToolType import ToolType
from cike_nexus.data.value_objects.McpToolConfigValue import StdioMcpToolConfigValue, HttpMcpToolConfigValue
from cike_nexus.data.value_objects.SkillToolConfigValue import SkillToolConfigValue


def _parse_config(v):
    if isinstance(v, dict):
        t = v.get("type")
        if t == ToolType.StdioMCP:
            return StdioMcpToolConfigValue(**v)
        elif t == ToolType.HttpMCP:
            return HttpMcpToolConfigValue(**v)
        elif t == ToolType.SKILL:
            return SkillToolConfigValue(**v)
    return v


# 3. 组合类型
ToolConfigType = Annotated[
    Union[StdioMcpToolConfigValue, HttpMcpToolConfigValue, SkillToolConfigValue],
    Field(discriminator="type"),
    BeforeValidator(_parse_config)
]


class Tool(FullAuditedEntity, table=True):
    name: str = Field(default="", description="名称", index=True, nullable=False, max_length=256)
    description: str = Field(default="", description="描述", index=True, nullable=False, max_length=512)
    type: ToolType = Field(default="", description="类型", index=True, nullable=False)
    config: ToolConfigType = Field(default=None, sa_column=Column(JSON))
    disabled: bool = Field(default=False, description="启用/禁用", index=True, nullable=False)
