from typing import Any

from pydantic import TypeAdapter
from sqlalchemy.types import JSON, TypeDecorator


class PydanticJsonType(TypeDecorator):
    """以 JSON 文本持久化 Pydantic 模型，读写两端都经过验证。

    impl 为 JSON：写入前用 TypeAdapter 校验并转成可 JSON 序列化的 dict，
    读取后还原为已验证的模型实例，避免把库里的裸 dict 当作已验证配置。
    """

    impl = JSON
    cache_ok = True

    def __init__(self, pydantic_type: Any, **kwargs: Any) -> None:
        self._adapter = TypeAdapter(pydantic_type)
        super().__init__(**kwargs)

    def process_bind_param(self, value: Any, dialect: Any) -> Any:
        if value is None:
            return None
        # dump_python 本身不校验，必须先 validate_python，否则裸 dict 的缺失或多余字段会被原样带过
        return self._adapter.dump_python(self._adapter.validate_python(value), mode="json")

    def process_result_value(self, value: Any, dialect: Any) -> Any:
        if value is None:
            return None
        return self._adapter.validate_python(value)
