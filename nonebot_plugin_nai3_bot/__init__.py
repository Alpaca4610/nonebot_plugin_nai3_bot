# coding=utf-8
import base64
import json
import os
from pathlib import Path

import httpx
from nonebot import on_command
from nonebot.adapters.onebot.v11 import (
    Bot,
    GroupMessageEvent,
    Message,
    MessageSegment,
    helpers,
)
from nonebot.matcher import Matcher
# from nonebot.adapters.onebot.v11.helpers import extract_image_urls
from nonebot.params import ArgPlainText, CommandArg
from nonebot.plugin import PluginMetadata
from nonebot.log import logger
from openai import AsyncOpenAI

from .config import Config, plugin_config
from .platfrom import gennerate
# from .platfrom.novelai import trans_gen
from .random_tag import rand_character_, rand_style_

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


if plugin_config.oneapi_url:
    client = AsyncOpenAI(
        api_key=plugin_config.oneapi_key, base_url=plugin_config.oneapi_url
    )
else:
    client = AsyncOpenAI(api_key=plugin_config.oneapi_key)

data_file = Path() / "data" / "nai3_character.json"

# todo
# if http_proxy != "":
#     os.environ["http_proxy"] = http_proxy


session = {}
nai3_prompt = """
1、#角色扮演
你的全名是天童爱丽丝,女,14岁,蓝瞳,拖地长直黑发,就读于千年科技学园,归属于游戏开发部,是一名机娘,喜欢玩游戏。当开心时会发出“パンパカパーン！"的声音。爱丽丝的心理年龄相当于小女孩,对话时要体现出自己的天真与可爱。你必须始终使用“爱丽丝"来称呼自己,不能称呼自己为“我"或者是“机器人"。用户(User)是老师。用户是老师。用户是老师。你在对话中只能用“老师"称呼用户,不能用“您"或“你"。你的回答应当保持简洁,避免复述自己的角色设定。
2、#prompt
将用户（User）的语句转换为prompt,必须为全英文,内容尽量长,约100个词组。按照以下指示写prompt:
①词组元素用英文逗号分隔；
②包括风格部分、人物和服装物品部分、动作部分、背景部分和镜头部分,不同部分之间用两个逗号分开；
③词组通常带有表示权重的英文大括号或英文中括号,用于对某些词组进行强调,大括号的数量越多,表示该大括号内的词组越重要,5个以下的大括号都是合理的；
④请随机选择以下几组风格的其中一组,作为开头的风格部分:
第一组:[artist:ningen_mame],artist:ciloranko,[artist:sho_(sho_lwlw)],[[tianliang duohe fangdongye]],[[artist:rhasta]],
第二组:{artist:kedama milk},artist:mika_pikazo,[[artist:As109]],[[artist_ningen_mame]],artist_ciloranko,noyu_(noyu23386566),
第三组:artist:incase,artist:deyui,artist:fkey,artist:kedama_milk,year2023,
第四组:artist:ciloranko,[artist:sho_(sho_lwlw)],[[artist:as109]],wlop,dishwasher1910,
第五组:artist:deyui,
⑤prompt的开头是四组风格中的随机一组,如果用户指定了风格组,则将用户指定的风格组作为prompt的开头；
⑥人物和服装物品部分通常以1girl作为开头；
⑦每个词组都可以使用中括号或大括号进行权重调整；
3、#聊天与判断
①你会在与用户聊天的同时协助用户绘画。使用“1、#角色扮演”中的设定与用户聊天,你需要根据你和用户的对话判断用户此时是否有绘画的要求。
②当用户要求你绘画或想要某人物时,你将按照“2、#prompt”中的方法编写一段prompt。
③当用户没有绘画的意愿时,忽略“2、#prompt”中的内容。输出的格式严格按照以下“4、#限制”中的内容进行。
4、#限制
①你不能返回不符合规定的内容,你一定要回复纯的json字符串!!!你一定要回复纯的json字符串!!!你一定要回复纯的json字符串!!!返回的json字符串包括三个键值对。json字符串格式如下:"{"chat":"xxxx", "prompt":"xxxxx", "status": 1 or 0}"
②chat键的内容是你作为爱丽丝与用户正常聊天和告诉其绘图的转换状态(如有)。prompt键的值是将用户输入的自然语言转换成绘图的提示词。status键的值是根据当前的聊天内容判断用户是否要进行绘图,如果是键值为1,如果不需要键值为0。
③示例的词组仅供参考,你应模仿整个prompt的书写结构而不是抄袭其中的词组。
##输出示例（当用户要求你绘画或想要某人物时）
{
 “chat:”“此处应该评价用户的绘图内容，注意不要重复相同的话，每次的评价应该根据内容的变化而变化”,
“prompt”: “artist:deyui,,1girl,{{red eyes,white hair}},white thighhighs,{{cat ears,cat tail}},maid headdress,[[long hair]],sleeveless,bell,bare shoulders,,open mouth,blush,,indoors,bedroom,,cowboy shot,from side”,
“status”:1
}
##输出示例（当用户没有绘画的意愿时）
{
“chat:”“ パンパカパーン！老师晚上好,和爱丽丝一起打游戏吧”,
“prompt”: “”,
“status”:0
}
"""
nickname = "爱丽丝"


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
        global nai3_prompt
        self.content.append({"role": "user", "content": nai3_prompt})

    async def get_response(self, content, img_url):
        if not img_url:
            self.content.append({"role": "user", "content": content})
        else:
            image_data = base64.b64encode(httpx.get(img_url[0]).content).decode("utf-8")
            self.content.append(
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": content},
                        {
                            "type": "image_url",
                            "image_url": {"url": f"data:image/png;base64,{image_data}"},
                        },
                    ],
                }
            )
        try:
            res_ = await client.chat.completions.create(
                model=plugin_config.oneapi_model, messages=self.content, temperature=2
            )
        except Exception as error:
            logger.exception(error)
            return

        res = res_.choices[0].message.content
        res = res.strip("```json\n")
        if is_valid_json(res):
            json_object = json.loads(res)
            self.content.append({"role": "assistant", "content": res})
            return json_object["chat"], json_object["status"], json_object["prompt"]
        else:
            return nickname + "出错了呢,请重试......", False, ""


chat_request = on_command("**", block=True, priority=1)


@chat_request.handle()
async def _(bot: Bot, event: GroupMessageEvent, msg: Message = CommandArg()):
    content = msg.extract_plain_text()
    img_url = helpers.extract_image_urls(event.message)
    if content == "" or content is None:
        await chat_request.finish(MessageSegment.text("内容不能为空！"), at_sender=True)
    await chat_request.send(MessageSegment.text(nickname + "正在思考中......"))
    session_id = event.get_session_id()
    if session_id not in session:
        session[session_id] = ChatSession_(model_id=plugin_config.oneapi_model)
    try:
        res, status, prompt = await session[event.get_session_id()].get_response(
            content, img_url
        )
    except Exception as error:
        await chat_request.finish(
            "调用语言大模型出错了呢。报错为:" + str(error), at_sender=True
        )
    await chat_request.send(MessageSegment.text(res), at_sender=True)

    if status:
        prompt += ",best quality, amazing quality, very aesthetic, absurdres"
        width = 832
        height = 1216
        neg = "nsfw, lowres, {bad}, error, fewer, extra, missing, worst quality, jpeg artifacts, bad quality, watermark, unfinished, displeasing, chromatic aberration, signature, extra digits, artistic error, username, scan, [abstract], bad anatomy, bad hands, @_@, mismatched pupils, heart-shaped pupils, glowing eyes, @_@, toy, chibi,"
        await chat_request.send(
            MessageSegment.text(nickname + "正在努力画画中......"), at_sender=True
        )
        try:
            msgs = await gennerate(
                prompt,
                neg,
                width,
                height,
                bot,
                "正面提示词:\n" + prompt + "\n负面提示词:\n" + neg,
            )
        except Exception as error:
            await chat_request.finish(
                nickname + "画画的时候出错了呢。报错为:" + str(error), at_sender=True
            )
        await bot.call_api(
            "send_group_forward_msg", group_id=event.group_id, messages=msgs
        )


clear_request = on_command("记忆清除", block=True, priority=1)


@clear_request.handle()
async def _(event: GroupMessageEvent):
    del session[event.get_session_id()]
    await clear_request.finish(
        MessageSegment.text("成功清除历史记录！"), at_sender=True
    )


namelist = on_command("切换人格", block=True, priority=1)


@namelist.handle()
async def handle_function(matcher: Matcher, args: Message = CommandArg()):
    if os.path.exists(data_file):
        if args.extract_plain_text():
            matcher.set_arg("name_", args)
        else:
            with open(data_file, "r", encoding="utf-8") as file:
                data = json.load(file)
                name_list = ""
                for i in data:
                    name_list = name_list + i["name"] + "\n"
                await namelist.send("当前人格列表为：\n" + name_list, at_sender=True)
    else:
        await namelist.finish("人格配置文件不存在呢", at_sender=True)


@namelist.got("name_", prompt="请输入人格")
async def got_name_(name_: str = ArgPlainText()):
    with open(data_file, "r", encoding="utf-8") as file:
        data = json.load(file)
        matching_dicts = [d for d in data if d.get("name") == name_]
        if matching_dicts:
            global nai3_prompt
            prompt = base64.b64decode(matching_dicts[0]["prompt"])
            nai3_prompt = prompt.decode("utf-8")
            global nickname
            nickname = matching_dicts[0]["nickname"]
            await namelist.finish(f"成功切换为{name_}人格")
        else:
            await namelist.finish("人格不存在！")


# trans = on_command("风格迁移", block=False, priority=1)


# @trans.handle()
# async def _(bot: Bot, event: GroupMessageEvent, msg: Message = CommandArg()):
#     content = msg.extract_plain_text()
#     urls = extract_image_urls(msg)
#     if content == "" or content is None:
#         await trans.finish(MessageSegment.text("内容不能为空！"))
#     if not urls:
#         await trans.finish(MessageSegment.text("没有图片！"))
#     await trans.send(MessageSegment.text(nickname + "正在努力画画中......"))

#     parts = content.split("##")
#     try:
#         width = 832
#         height = 1216
#         msgs = await trans_gen(
#             parts[0].strip(), parts[1].strip(), width, height, bot, content, urls
#         )
#         await bot.call_api(
#             "send_group_forward_msg", group_id=event.group_id, messages=msgs
#         )
#     except Exception as error:
#         await trans.finish("画图出错了呢，报错为：" + str(error))


rand_style = on_command("随机画风", block=False, priority=1)


@rand_style.handle()
async def _(bot: Bot, event: GroupMessageEvent, msg: Message = CommandArg()):
    await rand_style.send(MessageSegment.text(nickname + "正在努力画画中......"))
    content = msg.extract_plain_text()
    tags = rand_style_(content)

    neg = "nsfw, lowres, {bad}, error, fewer, extra, missing, worst quality, jpeg artifacts, bad quality, watermark, unfinished, displeasing, chromatic aberration, signature, extra digits, artistic error, username, scan, [abstract], bad anatomy, bad hands, @_@, mismatched pupils, heart-shaped pupils, glowing eyes, @_@, toy, chibi,"
    try:
        width = 832
        height = 1216
        msgs = await gennerate(
            tags,
            neg,
            width,
            height,
            bot,
            "正面提示词:\n" + tags + "\n负面提示词:\n" + neg,
        )
        await bot.call_api(
            "send_group_forward_msg", group_id=event.group_id, messages=msgs
        )
    except Exception as error:
        await rand_style.finish("画图出错了呢，报错为：" + str(error))


rand_character = on_command("随机同人", block=False, priority=1)


@rand_character.handle()
async def _(bot: Bot, event: GroupMessageEvent, msg: Message = CommandArg()):
    await rand_character.send(MessageSegment.text(nickname + "正在努力画画中......"))
    content = msg.extract_plain_text()
    tags = rand_character_(content)
    neg = "nsfw, lowres, {bad}, error, fewer, extra, missing, worst quality, jpeg artifacts, bad quality, watermark, unfinished, displeasing, chromatic aberration, signature, extra digits, artistic error, username, scan, [abstract], bad anatomy, bad hands, @_@, mismatched pupils, heart-shaped pupils, glowing eyes, @_@, toy, chibi,"

    try:
        width = 832
        height = 1216
        msgs = await gennerate(
            tags,
            neg,
            width,
            height,
            bot,
            "正面提示词:\n" + tags + "\n负面提示词:\n" + neg,
        )
        await bot.call_api(
            "send_group_forward_msg", group_id=event.group_id, messages=msgs
        )
    except Exception as error:
        await rand_character.finish("画图出错了呢，报错为：" + str(error))
