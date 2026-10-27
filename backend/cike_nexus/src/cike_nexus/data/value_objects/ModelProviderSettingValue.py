from abc import ABC
from typing import Annotated, Any, Literal, Union

from pydantic import BaseModel, Field, TypeAdapter

from cike_nexus.data.enums.ModelProviderType import ModelProviderType


class ModelProviderSettingValue(BaseModel, ABC):
    """模型提供者配置的公共字段。type 由子类以 Literal 收窄，不在此声明。"""

    api_key: str = Field(description="API 密钥")
    base_url: str = Field(default="", description="服务地址")
    timeout: int = Field(default=300, description="请求超时时间，单位秒")


class OpenAiProviderSettingValue(ModelProviderSettingValue):
    type: Literal[ModelProviderType.OpenAI] = Field(
        default=ModelProviderType.OpenAI, description="类型标识，固定为 OpenAI"
    )
    base_url: str = Field(default="https://api.openai.com/v1", description="服务地址")
    organization: str | None = Field(default=None, description="OpenAI 组织 ID")
    project: str | None = Field(default=None, description="OpenAI 项目 ID")


class AnthropicProviderSettingValue(ModelProviderSettingValue):
    type: Literal[ModelProviderType.Anthropic] = Field(
        default=ModelProviderType.Anthropic, description="类型标识，固定为 Anthropic"
    )
    base_url: str = Field(default="https://api.anthropic.com", description="服务地址")
    api_version: str = Field(default="2023-06-01", description="Anthropic API 版本")


ModelProviderSettingType = Annotated[
    Union[OpenAiProviderSettingValue, AnthropicProviderSettingValue],
    Field(discriminator="type"),
]

model_provider_setting_adapter = TypeAdapter(ModelProviderSettingType)


def parse_model_provider_setting(value: Any) -> ModelProviderSettingValue | None:
    """把 dict 或值对象规范化为已验证的 Setting 实例；None 原样返回。"""
    if value is None:
        return None
    return model_provider_setting_adapter.validate_python(value)
