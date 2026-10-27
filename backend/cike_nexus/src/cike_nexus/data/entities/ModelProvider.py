from sqlalchemy import Column
from sqlmodel import Field

from cike_nexus.data.abstracts.FullAuditedEntity import FullAuditedEntity
from cike_nexus.data.enums.ModelProviderType import ModelProviderType
from cike_nexus.data.PydanticJsonType import PydanticJsonType
from cike_nexus.data.value_objects.ModelProviderSettingValue import (
    ModelProviderSettingType,
    parse_model_provider_setting,
)


class ModelProvider(FullAuditedEntity, table=True):
    name: str = Field(default="", description="模型提供者名称", index=True, nullable=False, max_length=256)
    type: ModelProviderType = Field(description="类型", index=True, nullable=False)
    setting: ModelProviderSettingType = Field(
        description="配置，内容随类型不同而不同",
        sa_column=Column(PydanticJsonType(ModelProviderSettingType), nullable=False),
    )

    def __init__(self, **data):
        # table=True 模型的 __init__ 跳过 Pydantic 校验，这里显式规范化，
        # 保证内存实例的 type 是枚举、setting 是已验证的值对象，且两者一致。
        if data.get("type") is not None:
            data["type"] = ModelProviderType(data["type"])
        if data.get("setting") is not None:
            data["setting"] = parse_model_provider_setting(data["setting"])
            if data.get("type") is not None and data["type"] is not data["setting"].type:
                raise ValueError("type 与 setting.type 不一致")
        super().__init__(**data)
