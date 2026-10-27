from typing import Annotated, Any

from pydantic import Field, TypeAdapter

from cike_nexus.data.value_objects.McpToolConfigValue import (
    HttpMcpToolConfigValue,
    StdioMcpToolConfigValue,
)
from cike_nexus.data.value_objects.SkillToolConfigValue import SkillToolConfigValue


ToolConfigType = Annotated[
    StdioMcpToolConfigValue | HttpMcpToolConfigValue | SkillToolConfigValue,
    Field(discriminator="type"),
]

tool_config_adapter = TypeAdapter(ToolConfigType)


def parse_tool_config(value: Any) -> ToolConfigType:
    """按 type 标签将配置字典或值对象规范化，拒绝空配置与非法结构。"""
    return tool_config_adapter.validate_python(value)
