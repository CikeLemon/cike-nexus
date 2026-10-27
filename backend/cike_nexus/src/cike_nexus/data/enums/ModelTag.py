from enum import Enum


class ModelTag(str, Enum):
    """模型支持的内容形态标签，可叠加：一个模型可同时支持文本和图片。

    成员名必须与值一致：落库前经 Pydantic 序列化，取的是值。
    """

    Text = "Text"
    Image = "Image"
    Audio = "Audio"
    Video = "Video"
