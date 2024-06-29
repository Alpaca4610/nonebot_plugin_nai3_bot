import base64
import html
import random

import httpx
from nonebot.adapters.onebot.v11 import (
    MessageSegment,
)

from ..config import plugin_config


async def gennerate(pos, neg, width, height, bot, content_):
    assert isinstance(plugin_config.sd_api, str)

    seed = random.randint(0, 2**32 - 1)

    payload = plugin_config.sd_config.copy()
    payload.update(
        {
            "seed": seed,
            "prompt": pos,
            "negative_prompt": neg,
            "width": width,
            "height": height,
            "send_images": True,
            "save_images": False,
        }
    )

    async with httpx.AsyncClient() as client:
        response = await client.post(plugin_config.sd_api, json=payload)
        content = response.json()
        img = base64.b64decode(content["images"][0])

        msgs = []
        temp = {
            "type": "node",
            "data": {
                "name": "StableDiffusion",
                "uin": bot.self_id,
                "content": MessageSegment.image(img)
                + MessageSegment.text(html.unescape(content_)),
            },
        }
        temp2 = {
            "type": "node",
            "data": {
                "name": "StableDiffusion",
                "uin": bot.self_id,
                "content": MessageSegment.text("seed:" + str(seed)),
            },
        }
        msgs.append(temp)
        msgs.append(temp2)
        return msgs
