from pydantic import Extra, BaseModel
from typing import Optional


class Config(BaseModel, extra=Extra.ignore):
    nai3_token: Optional[str] = ""  # （必填）NovelAI的token
    oneapi_key: Optional[str] = ""  # （必填）OpenAI官方或者是支持OneAPI的大模型中转服务商提供的KEY
    oneapi_url: Optional[str] = ""  # （可选）大模型中转服务商提供的中转地址，使用OpenAI官方服务不需要填写
    oneapi_model: Optional[str] = "gpt-4" # （可选）使用的语言大模型，建议使用gpt4或gpt4o模型以达到更好的体验效果

class ConfigError(Exception):
    pass
