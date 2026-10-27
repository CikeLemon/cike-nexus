from typing import Any

from sqlalchemy import Column
from sqlmodel import Field

from cike_nexus.data.abstracts.FullAuditedEntity import FullAuditedEntity
from cike_nexus.data.enums.ToolType import ToolType
from cike_nexus.data.PydanticJsonType import PydanticJsonType
from cike_nexus.data.value_objects.ToolConfigValue import ToolConfigType, parse_tool_config


class Tool(FullAuditedEntity, table=True):
    name: str = Field(default="", description="名称", index=True, nullable=False, max_length=256)
    description: str = Field(default="", description="描述", index=True, nullable=False, max_length=512)
    type: ToolType = Field(description="类型", index=True, nullable=False)
    config: ToolConfigType = Field(
        description="工具配置，结构由工具类型决定",
        sa_column=Column(PydanticJsonType(ToolConfigType), nullable=False),
    )
    disabled: bool = Field(default=False, description="启用/禁用", index=True, nullable=False)

    def __init__(self, **data: Any) -> None:
        # table=True 的构造跳过 Pydantic 校验，显式规范化枚举与配置值对象。
        if data.get("type") is not None:
            data["type"] = ToolType(data["type"])
        if data.get("config") is not None:
            data["config"] = parse_tool_config(data["config"])
        super().__init__(**data)

    def model_post_init(self, context: Any) -> None:
        # 初始化完成后再检查，兼容 model_validate 内部的无参初始化。
        super().model_post_init(context)
        if getattr(self, "type", None) is None:
            raise ValueError("工具类型不能为空")
        if getattr(self, "config", None) is None:
            raise ValueError("工具配置不能为空")
        if self.type is not self.config.type:
            raise ValueError("type 与 config.type 不一致")
