from typing import Annotated

from pydantic import BeforeValidator
from sqlalchemy import JSON
from sqlmodel import Field, Column

from cike_nexus.data.abstracts.FullAuditedEntity import FullAuditedEntity
from cike_nexus.data.value_objects.ModelConfigValue import ModelConfigValue


def _parse_config(v):
    if isinstance(v, dict):
        return ModelConfigValue(**v)
    return v


ModelConfig = Annotated[
    ModelConfigValue,
    Field(discriminator="type"),
    BeforeValidator(_parse_config)
]


class AgentApplication(FullAuditedEntity, table=True):
    display_name: str = Field(default="", description="显示名称", index=True, nullable=False, max_length=256)
    name: str = Field(default="", description="名称", index=True, nullable=False, max_length=256)
    description: str = Field(default="", description="描述", index=True, nullable=False, max_length=512)
    avatar: str = Field(default="", description="头像地址", nullable=False, max_length=256)
    instructions: str = Field(default="", description="提示词", nullable=False)
    default_model: ModelConfig = Field(description="默认模型", sa_column=Column(JSON))
