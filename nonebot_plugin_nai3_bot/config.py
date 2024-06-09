from typing import Dict, Optional

import nonebot
from pydantic import BaseModel, Extra, validator


class Config(BaseModel, extra=Extra.ignore):
    nai3_token: Optional[str] = ""  # （可选）NovelAI的token
    sd_api: Optional[str] = ""  # （可选）StableDiffusion的api
    sd_config: Dict = {
        "batch_size": 1,
        "steps": 28,
        "cfg_scale": 5,
        "send_images": True,
        "save_images": False,
    }  # （可选）StableDiffusion的config
    oneapi_key: str = (
        ""  # （必填）OpenAI官方或者是支持OneAPI的大模型中转服务商提供的KEY
    )
    oneapi_url: Optional[str] = (
        ""  # （可选）大模型中转服务商提供的中转地址，使用OpenAI官方服务不需要填写
    )
    oneapi_model: Optional[str] = (
        "gpt-4"  # （可选）使用的语言大模型，建议使用gpt4或gpt4o模型以达到更好的体验效果
    )

    @validator("nai3_token", pre=True)
    def _token(cls, v, values):
        assert v or values.get(
            "sd_api"
        ), "请配置 NovelAI的token 或 StableDiffusion的api"
        return v

    @validator("oneapi_key")
    def _oneapi_key(cls, v):
        assert v, "请配置大模型使用的KEY"
        return v


plugin_config = Config.parse_obj(nonebot.get_driver().config.dict())
