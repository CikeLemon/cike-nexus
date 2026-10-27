from abc import ABC
from typing import Literal

from pydantic import BaseModel, Field

from cike_nexus.data.enums.ToolType import ToolType


class McpToolConfigValue(BaseModel, ABC):
    """MCP 配置基类，具体传输类型由子类的 Literal 标识。"""

class StdioMcpToolConfigValue(McpToolConfigValue):
    type: Literal[ToolType.StdioMCP] = Field(
        default=ToolType.StdioMCP, description="类型标识，固定为 StdioMCP"
    )
    command: str = Field(description="启动 MCP 服务的命令")
    args: list[str] = Field(description="命令行参数")
    env: dict[str, str] = Field(description="进程环境变量，可能包含敏感凭据")


class HttpMcpToolConfigValue(McpToolConfigValue):
    type: Literal[ToolType.HttpMCP] = Field(
        default=ToolType.HttpMCP, description="类型标识，固定为 HttpMCP"
    )
    url: str = Field(description="MCP 服务地址")
    headers: dict[str, str] = Field(description="HTTP 请求头，可能包含敏感凭据")
    timeout: int = Field(description="请求超时时间，单位秒")