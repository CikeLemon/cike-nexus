from enum import Enum


class ToolType(str, Enum):
    """工具类型。保留成员名和值，兼容既有数据库枚举与 JSON 标签。"""

    StdioMCP = "StdioMCP"
    HttpMCP = "HttpMCP"
    SKILL = "SKILL"
