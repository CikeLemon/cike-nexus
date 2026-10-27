from pydantic import TypeAdapter
from sqlalchemy import BigInteger, Column
from sqlmodel import Field

from cike_nexus.data.abstracts.FullAuditedEntity import FullAuditedEntity
from cike_nexus.data.enums.ModelTag import ModelTag
from cike_nexus.data.PydanticJsonType import PydanticJsonType

model_tag_list_adapter = TypeAdapter(list[ModelTag])


class ModelEntity(FullAuditedEntity, table=True):
    # 类名避开 Pydantic 的 model_ 保护命名空间，表名保留业务语义
    __tablename__ = "model"

    provider_id: int = Field(default=0, description="所属模型提供商 ID", index=True, nullable=False,
                             sa_type=BigInteger)
    name: str = Field(default="", description="调用提供商时使用的模型标识，如 gpt-4o", index=True, nullable=False,
                      max_length=256)
    display_name: str = Field(default="", description="显示名称", nullable=False, max_length=256)
    description: str = Field(default="", description="描述", nullable=False, max_length=512)
    tags: list[ModelTag] = Field(
        default_factory=list,
        description="支持的内容形态标签，如纯文本、图片",
        sa_column=Column(PydanticJsonType(list[ModelTag]), nullable=False),
    )
    disabled: bool = Field(default=False, description="启用/禁用", index=True, nullable=False)

    def __init__(self, **data):
        # table=True 模型的 __init__ 跳过 Pydantic 校验，这里显式规范化，
        # 保证内存实例的 tags 是枚举成员列表，而不是原样带过的字符串。
        if data.get("tags") is not None:
            data["tags"] = model_tag_list_adapter.validate_python(data["tags"])
        super().__init__(**data)
