from enum import Enum


class ModelProviderType(str, Enum):
    """模型提供者类型。成员名必须与值一致：SQLAlchemy 落库写入的是成员名。"""

    OpenAI = "OpenAI"
    Anthropic = "Anthropic"
