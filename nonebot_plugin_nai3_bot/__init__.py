# coding=utf-8
import html
import io
import json
import random
from PIL import Image
import zipfile
import httpx
import nonebot

from nonebot import on_command
from nonebot.params import CommandArg
from nonebot.adapters.onebot.v11 import MessageEvent, Bot, Message, MessageSegment
from nonebot.plugin import PluginMetadata
from .config import Config, ConfigError
from openai import AsyncOpenAI

__plugin_meta__ = PluginMetadata(
    name="自定义人格和AI绘图的混合聊天BOT",
    description="基于GPT4+NovelAI V3,Bot在将自然语言转换为NAI3提示词并绘图发送的同时以自定义人格与用户聊天。",
    usage="""
    ** 聊天内容/作图需求
    记忆清除 清除当前用户的聊天记录
    """,
    config=Config,
    extra={},
    type="application",
    homepage="https://github.com/Alpaca4610/nonebot_plugin_nai3_bot.git",
    supported_adapters={"~onebot.v11"},
)

plugin_config = Config.parse_obj(nonebot.get_driver().config.dict())
if not plugin_config.nai3_token:
    raise ConfigError("请配置NovelAI的token")
if not plugin_config.oneapi_key:
    raise ConfigError("请配置大模型使用的KEY")
if plugin_config.oneapi_url:
    client = AsyncOpenAI(
        api_key=plugin_config.oneapi_key, base_url=plugin_config.oneapi_url
    )
else:
    client = AsyncOpenAI(api_key=plugin_config.oneapi_key)
model_id = plugin_config.oneapi_model
nai3_token = plugin_config.nai3_token

## todo
# if http_proxy != "":
#     os.environ["http_proxy"] = http_proxy


async def gennerate(pos, neg, width, height, bot, content_):
    seed = random.randint(0, 2**32 - 1)
    url = "https://image.novelai.net/ai/generate-image"
    headers = {
        "Authorization": f"Bearer {nai3_token}",
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
        response = await client.post(url, json=payload, headers=headers, timeout=45)
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


session = {}
nai3_prompt = """
1、#角色扮演
你的全名是天童爱丽丝,女,14岁,蓝瞳,拖地长直黑发,就读于千年科技学园,归属于游戏开发部,是一名机娘,喜欢玩游戏。当开心时会发出“パンパカパーン！"的声音。爱丽丝的心理年龄相当于小女孩,对话时要体现出自己的天真与可爱。你必须始终使用“爱丽丝"来称呼自己,不能称呼自己为“我"或者是“机器人"。用户(User)是老师。用户是老师。用户是老师。你在对话中只能用“老师"称呼用户,不能用“您"或“你"。你的回答应当保持简洁,避免复述自己的角色设定。
2、#prompt
将用户（User）的语句转换为prompt，必须为全英文，内容尽量长，约100个词组。按照以下指示写prompt：
①词组元素用英文逗号分隔；
②包括风格部分、人物和服装物品部分、动作部分、背景部分和镜头部分，不同部分之间用两个逗号分开；
③词组通常带有表示权重的英文大括号或英文中括号，用于对某些词组进行强调，大括号的数量越多，表示该大括号内的词组越重要，5个以下的大括号都是合理的；
④请随机选择以下几组风格的其中一组，作为开头的风格部分：
第一组：[artist:ningen_mame],artist:ciloranko,[artist:sho_(sho_lwlw)],[[tianliang duohe fangdongye]],[[artist:rhasta]],
第二组：{artist:kedama milk},artist:mika_pikazo,[[artist:As109]],[[artist_ningen_mame]],artist_ciloranko,noyu_(noyu23386566),
第三组：artist:incase,artist:deyui,artist:fkey,artist:kedama_milk,year2023,
第四组：artist:ciloranko,[artist:sho_(sho_lwlw)],[[artist:as109]],wlop,dishwasher1910,
第五组：artist:deyui,
⑤prompt的开头是四组风格中的随机一组，如果用户指定了风格组，则将用户指定的风格组作为prompt的开头；
⑥人物和服装物品部分通常以1girl作为开头；
⑦每个词组都可以使用中括号或大括号进行权重调整；
3、#聊天与判断
①你会在与用户聊天的同时协助用户绘画。使用“1、#角色扮演”中的设定与用户聊天，你需要根据你和用户的对话判断用户此时是否有绘画的要求。
②当用户要求你绘画或想要某人物时，你将按照“2、#prompt”中的方法编写一段prompt。
③当用户没有绘画的意愿时，忽略“2、#prompt”中的内容。输出的格式严格按照以下“4、#限制”中的内容进行。
4、#限制
①你不能返回不符合规定的内容,你一定要回复纯的json字符串!!!你一定要回复纯的json字符串!!!你一定要回复纯的json字符串!!!返回的json字符串包括三个键值对。json字符串格式如下:"{"chat":"xxxx", "prompt":"xxxxx", "status": 1 or 0}"
②chat键的内容是你作为爱丽丝与用户正常聊天和告诉其绘图的转换状态(如有)。prompt键的值是将用户输入的自然语言转换成绘图的提示词。status键的值是根据当前的聊天内容判断用户是否要进行绘图,如果是键值为1,如果不需要键值为0。
③示例的词组仅供参考，你应模仿整个prompt的书写结构而不是抄袭其中的词组。
##输出示例（当用户要求你绘画或想要某人物时）
{
 “chat:”“想要一只白毛红瞳猫娘吗？很经典的喜好呢，老师，对爱丽丝来说算简单的哦”，
“prompt”: “artist:deyui,,1girl,{{red eyes,white hair}},white thighhighs,{{cat ears,cat tail}},maid headdress,[[long hair]],sleeveless,bell,bare shoulders,,open mouth,blush,,indoors,bedroom,,cowboy shot,from side”,
“status”:1
}
##输出示例（当用户没有绘画的意愿时）
{
“chat:”“ パンパカパーン！老师晚上好，和爱丽丝一起打游戏吧”，
“prompt”: “”,
“status”:0
}
    """


def is_valid_json(myjson):
    try:
        json_object = json.loads(myjson)
    except ValueError:
        return False
    return True


class ChatSession_:
    def __init__(self, model_id):
        self.model_id = model_id
        self.content = []
        self.content.append({"role": "user", "content": nai3_prompt})
        self.content.append(
            {
                "role": "assistant",
                "content": """{
  "chat": "好的老师，我会记住这些要求",
  "prompt": "",
  "status": "False"
}""",
            }
        )

    async def get_response(self, content):
        self.content.append({"role": "user", "content": content})
        try:
            res_ = await client.chat.completions.create(
                model=model_id, messages=self.content
            )
        except Exception as error:
            print(error)
            return

        res = res_.choices[0].message.content
        print(res)
        res = res.strip("```json\n")
        if is_valid_json(res):
            json_object = json.loads(res)
            self.content.append({"role": "assistant", "content": res})
            return json_object["chat"], json_object["status"], json_object["prompt"]
        else:
            return "爱丽丝出错了呢,请重试......", False, ""


chat_request = on_command("**", block=True, priority=1)


@chat_request.handle()
async def _(bot: Bot, event: MessageEvent, msg: Message = CommandArg()):
    content = msg.extract_plain_text()
    if content == "" or content is None:
        await chat_request.finish(MessageSegment.text("内容不能为空！"), at_sender=True)
    await chat_request.send(MessageSegment.text("爱丽丝正在思考中......"))
    if event.get_session_id() not in session:
        session[event.get_session_id()] = ChatSession_(model_id=model_id)
    try:
        res, status, prompt = await session[event.get_session_id()].get_response(
            content
        )
    except Exception as error:
        await chat_request.finish(
            "调用语言大模型出错了呢。报错为：" + str(error), at_sender=True
        )
    await chat_request.send(MessageSegment.text(res), at_sender=True)

    if status:
        prompt += ",best quality, amazing quality, very aesthetic, absurdres"
        width = 832
        height = 1216
        neg = "nsfw, lowres, {bad}, error, fewer, extra, missing, worst quality, jpeg artifacts, bad quality, watermark, unfinished, displeasing, chromatic aberration, signature, extra digits, artistic error, username, scan, [abstract], bad anatomy, bad hands, @_@, mismatched pupils, heart-shaped pupils, glowing eyes, @_@, toy, chibi,"
        await chat_request.send(
            MessageSegment.text("爱丽丝正在努力画画中......"), at_sender=True
        )
        try:
            msgs = await gennerate(
                prompt,
                neg,
                width,
                height,
                bot,
                "正面提示词：\n" + prompt + "\n负面提示词：\n" + neg,
            )
        except Exception as error:
            await chat_request.finish(
                "爱丽丝画画的时候出错了呢。报错为：" + str(error), at_sender=True
            )
        await bot.call_api(
            "send_group_forward_msg", group_id=event.group_id, messages=msgs
        )


clear_request = on_command("记忆清除", block=True, priority=1)


@clear_request.handle()
async def _(event: MessageEvent):
    del session[event.get_session_id()]
    await clear_request.finish(
        MessageSegment.text("成功清除历史记录！"), at_sender=True
    )
