import base64
import html
import io
import json
import random
import zipfile

import httpx
from nonebot.adapters.onebot.v11 import (
    MessageSegment,
)
from PIL import Image

from ..config import plugin_config

async def image_to_base64(url):
    async with httpx.AsyncClient() as client:
        response = await client.post(url,timeout=30)
        image_content = response.content
        base64_image = base64.b64encode(image_content)
        return base64_image.decode('utf-8')

async def gennerate(pos, neg, width, height, bot, content_):
    seed = random.randint(0, 2**32 - 1)
    url = "https://image.novelai.net/ai/generate-image"
    headers = {
        "Authorization": f"Bearer {plugin_config.nai3_token}",
        "Content-Type": "application/json",
        "Origin": "https://novelai.net",
        "Referer": "https://novelai.net/",
    }

    payload = {
        "action": "generate",
        "input": pos,
        "model": "nai-diffusion-3",
        "parameters": {
            "width": width,
            "height": height,
            "scale": 5,
            "sampler": "k_dpmpp_2s_ancestral",
            "steps": 28,
            "n_samples": 1,
            "ucPreset": 0,
            "add_original_image": False,
            "cfg_rescale": 0,
            "controlnet_strength": 1,
            "dynamic_thresholding": False,
            "legacy": False,
            "negative_prompt": neg,
            "noise_schedule": "native",
            "qualityToggle": True,
            "seed": seed,
            "sm": True,
            "sm_dyn": False,
            "uncond_scale": 1,
        },
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(url, json=payload, headers=headers, timeout=30)
        zipfile_in_memory = io.BytesIO(response.content)
        with zipfile.ZipFile(zipfile_in_memory, "r") as zip_ref:
            file_names = zip_ref.namelist()
            if file_names:
                with zip_ref.open(file_names[0]) as file:
                    image = Image.open(file)
                    buffered = io.BytesIO()
                    image.save(buffered, format="PNG")
                    info_ = json.loads(image.info["Comment"])
                    # text_ = "AI绘图 " + content_
                    msgs = []
                    temp = {
                        "type": "node",
                        "data": {
                            "name": "NovelAI",
                            "uin": bot.self_id,
                            "content": MessageSegment.image(buffered)
                            + MessageSegment.text(html.unescape(content_)),
                        },
                    }
                    temp2 = {
                        "type": "node",
                        "data": {
                            "name": "NovelAI",
                            "uin": bot.self_id,
                            "content": MessageSegment.text("seed:" + str(info_["seed"])),
                        },
                    }
                    msgs.append(temp)
                    msgs.append(temp2)
                    return msgs
            
async def trans_gen(pos,neg,width,height,bot,content,pic_url):
    seed = random.randint(0, 2**32 - 1)
    url = "https://image.novelai.net/ai/generate-image"
    img_lists = []
    for i in pic_url:
        print(i)
        pic = await image_to_base64(i)
        img_lists.append(pic)
        
    reference_strength_multiple = [0.8 for _ in img_lists]
    reference_information_extracted_multiple = [0.45 for _ in img_lists]
    headers = {
        "Authorization": f"Bearer {plugin_config.nai3_token}",
        "Content-Type": "application/json",
        "Origin": "https://novelai.net",
        "Referer": "https://novelai.net/"
    }

    payload = {
        "action": "generate",
        "input": pos,
        "model": "nai-diffusion-3",
        "parameters": {
            "width": width,
            "height": height,
            "scale": 5,
            "sampler": "k_dpmpp_2s_ancestral",
            "steps": 28,
            "n_samples": 1,
            "ucPreset": 0,
            "add_original_image": False,
            "cfg_rescale": 0,
            "controlnet_strength": 1,
            "dynamic_thresholding": False,
            "legacy": False,
            "negative_prompt": neg,
            "noise_schedule": "native",
            "qualityToggle": True,
            "seed": seed,
            "sm": True,
            "sm_dyn": False,
            "uncond_scale": 1,
            "reference_image_multiple":img_lists,
            "reference_information_extracted_multiple": reference_information_extracted_multiple,
            "reference_strength_multiple": reference_strength_multiple
        }
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(url, json=payload, headers=headers, timeout=30)
        zipfile_in_memory = io.BytesIO(response.content)
        with zipfile.ZipFile(zipfile_in_memory, 'r') as zip_ref:
            file_names = zip_ref.namelist()
            if file_names:
                with zip_ref.open(file_names[0]) as file:
                    image = Image.open(file)
                    buffered = io.BytesIO()
                    image.save(buffered, format="PNG")
                    info_ = json.loads(image.info["Comment"])
                    text_ = "风格迁移 " + content
                    msgs = []
                    temp = {
                        "type": "node",
                        "data": {
                        "name": "NovelAI",
                        "uin": bot.self_id,
                        "content": MessageSegment.image(buffered) + MessageSegment.text(html.unescape(text_))
                        }
                    }
                    temp2 = {
                        "type": "node",
                        "data": {
                        "name": "NovelAI",
                        "uin": bot.self_id,
                        "content": MessageSegment.text("seed:" + str(info_["seed"]))
                        }
                    }
                    msgs.append(temp)
                    msgs.append(temp2)
                    return msgs