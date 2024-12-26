import json
import httpx
import io
import zipfile
import json

from PIL import Image
from random import randint
from nonebot.log import logger
from ..config import plugin_config

async def generate_image(input_text, character_prompts):
    url = "https://image.novelai.net/ai/generate-image"
    headers = {
        "accept": "*/*",
        "accept-language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
        "authorization": f"Bearer {plugin_config.nai3_token}",
        "content-type": "application/json",
        "origin": "https://novelai.net",
        "referer": "https://novelai.net/",
        "sec-ch-ua": '"Microsoft Edge";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"',
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-site",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36 Edg/131.0.0.0",
    }
    payload = {
        "input": input_text,
        "model": "nai-diffusion-4-curated-preview",
        "action": "generate",
        "parameters": {
            "params_version": 3,
            "width": 832,
            "height": 1216,
            "scale": 6,
            "sampler": "k_euler_ancestral",
            "steps": 30,
            "n_samples": 1,
            "ucPreset": 0,
            "qualityToggle": True,
            "dynamic_thresholding": False,
            "controlnet_strength": 1,
            "legacy": False,
            "add_original_image": True,
            "cfg_rescale": 0,
            "noise_schedule": "karras",
            "legacy_v3_extend": False,
            "use_coords": False,
            "seed": randint(0, 2**32 - 1),
            "characterPrompts": character_prompts,
            "v4_prompt": {
                "caption": {
                    "base_caption": input_text,
                    "char_captions": [
                        {
                            "char_caption": char["prompt"],
                            "centers": [{"x": char["center"]["x"], "y": char["center"]["y"]}],
                        }
                        for char in character_prompts
                    ],
                },
                "use_coords": False,
                "use_order": True,
            },
            "v4_negative_prompt": {
                "caption": {
                    "base_caption": "blurry, lowres, error, film grain, scan artifacts, worst quality, bad quality, jpeg artifacts, very displeasing, chromatic aberration, logo, dated, signature, multiple views, gigantic breasts",
                    "char_captions": [
                        {"char_caption": "", "centers": [{"x": 0, "y": 0}]}
                        for _ in character_prompts
                    ],
                }
            },
            "negative_prompt": "blurry, lowres, error, film grain, scan artifacts, worst quality, bad quality, jpeg artifacts, very displeasing, chromatic aberration, logo, dated, signature, multiple views, gigantic breasts",
            "reference_image_multiple": [],
            "reference_information_extracted_multiple": [],
            "reference_strength_multiple": [],
            "deliberate_euler_ancestral_bug": False,
            "prefer_brownian": True,
        },
    }

    timeout = httpx.Timeout(60.0)  # 设置超时时间为 60 秒
    async with httpx.AsyncClient(timeout=timeout) as client:
        try:
            response = await client.post(url, json=payload, headers=headers)
            if response.status_code != 200:
                raise Exception(
                    f"Error: Received status code {response.status_code}. Response Text: {response.text}")

            zipfile_in_memory = io.BytesIO(response.content)
            with zipfile.ZipFile(zipfile_in_memory, "r") as zip_ref:
                file_names = zip_ref.namelist()
                if not file_names:
                    raise Exception("ZIP file is empty.")

                logger.info(f"Files in ZIP: {file_names}")
                with zip_ref.open(file_names[0]) as file:
                    image = Image.open(file)
                    buffered = io.BytesIO()
                    image.save(buffered, format="PNG")

                    if "Comment" in image.info:
                        info_ = json.loads(image.info["Comment"])
                        logger.info(f"Image Comment Info: {info_}")
                        return buffered, info_
                    else:
                        raise Exception(
                            "No 'Comment' field found in image metadata.")

        except zipfile.BadZipFile:
            raise Exception("Failed to parse ZIP file from response.")
        except ValueError:
            raise Exception("Failed to parse JSON from image comment.")
        except httpx.RequestError as exc:
            raise Exception(f"An error occurred while requesting: {exc}")
