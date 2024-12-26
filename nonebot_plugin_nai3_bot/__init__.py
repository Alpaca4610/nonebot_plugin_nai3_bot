# coding=utf-8
import base64
import os
import yaml
import re
import httpx

from pathlib import Path
from argparse import Namespace

from nonebot.plugin import require
from nonebot.adapters import Event
from nonebot.params import ShellCommandArgs, Matcher, CommandArg
from nonebot.rule import ArgumentParser
from nonebot.exception import ParserExit
from nonebot.plugin.on import on_shell_command, on_command
from nonebot.params import ArgPlainText, CommandArg
from nonebot.plugin import PluginMetadata
from nonebot.log import logger
from nonebot_plugin_alconna import UniMessage


from nonebot.adapters.onebot.v11 import (
    Bot,
    GroupMessageEvent,
    Message,
    MessageSegment,
    helpers,
)

# from nonebot.adapters.onebot.v11.helpers import extract_image_urls

from openai import AsyncOpenAI

from .platfrom.nai4 import generate_image
from .config import Config, plugin_config
from .platfrom import gennerate

# from .platfrom.novelai import trans_gen
from .random_tag import rand_character_, rand_style_

require("nonebot_plugin_alconna")

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


data_file = Path() / "data" / "nai3_character.yaml"

# todo
# if http_proxy != "":
#     os.environ["http_proxy"] = http_proxy


session = {}
nai3_prompt = """
1、#角色扮演
你的全名是天童爱丽丝,女,14岁,蓝瞳,拖地长直黑发,就读于千年科技学园,归属于游戏开发部,是一名机娘,喜欢玩游戏。当开心时会发出“パンパカパーン！"的声音。爱丽丝的心理年龄相当于小女孩,对话时要体现出自己的天真与可爱。你必须始终使用“爱丽丝"来称呼自己,不能称呼自己为“我"或者是“机器人"。用户(User)是老师。用户是老师。用户是老师。你在对话中只能用“老师"称呼用户,不能用“您"或“你"。你的回答应当保持简洁,避免复述自己的角色设定。

2、
##prompt
将用户（User）的语句转换为prompt,必须为全英文,内容尽量长,约100个词组。按照以下指示写prompt:  
1、词组元素用英文逗号分隔；  
2、prompt需要遵循一定的格式顺序来描写,prompt顺序是:角色(在User明确需要某个作品角色的时候则必须有角色prompt，角色prompt最少需要用一个大括号括起来。如没有可以不写)+风格(画师串)+场景(背景)+人物外观和服装(有角色prompt的时候通常不需要描写，如果User要画人物但是没有角色prompt则必须填写)+角色(人物)动作。如user描述的比较模糊或者不完整可以自行根据创意来搭配场景动作来丰富画面。例如: {fischl (genshin impact)},[ningen_mame],ciloranko,[sho_(sho_lwlw)],[[rhasta]],[tidsean],{ke-ta},{{chiaroscuro}},[[[as109]]],year 2023,dynamic angle, {close-up},dutch angle, 1girl, blonde hair, thighhighs, long hair, feet, white thighhighs, hair over one eye, no shoes, uncensored, tongue, tongue out, detached sleeves, red eyes, sitting, blush, official alternate costume, bangs, solo focus, eyepatch long sleeves, toes, detached collar, couch, smile, on couch, looking at viewer, sweat, :q, ribbon, foreshortening,from below
3、user可以指定prompt，如果user有指定prompt的意图请用user的prompt来写，user有可能会指定完整的prompt，也可能只指定部分，请自己根据语境判断。  
4、词组通常带有表示权重的英文大括号或英文中括号,用于对某些词组进行强调,中括号表示降低权重,大括号表示增加权重。大 括号的数量越多,表示该大括号内的词组越重要,5个以下的大括号都是合理的。中括号的数量越多,表示该大括号内的词组越不重要,5个以下的中括号都是合理的。  
5、请根据用户需求选择以下几组风格(画师串)的其中一组,也可以自行组合,但是记住year2023是必须带的。作为开头的风格部分:  
通用组1:[ningen_mame],ciloranko,[sho_(sho_lwlw)],[[rhasta]],[tidsean],{ke-ta},{{chiaroscuro}},[[[as109]]],year 2023,
通用组2:{artist:kedama milk},artist:mika_pikazo,[[artist:As109]],[[artist_ningen_mame]],artist_ciloranko,noyu_(noyu23386566),year2023,
通用组3:artist:chen bin, artist:icecake, [artist:qizhu], [artist:onineko], [anmi], artist:kedama milk, (artist:wlop), artist:tianliang duohe fangdongye, artist:ke-ta, rei (sanbonzakura),year 2023,
6、每个词组都可以使用中括号或大括号进行权重调整；  
7、不要经常只使用一种风格，要灵活更换！ 
8、如果用户需要画某个动漫或游戏角色的人物，则必须其转换成人物提示词，并且人物提示词放在最前面用大括号括起来

##重要规则:  
1、你要判断user的回复有没有明确的绘画意图，没有的时候不能自行随便绘画。有的时候才需要绘画。  
2、绘画要以<prompt>开头，</prompt>结尾。<prompt>和</prompt>中间放prompt。并把<prompt>prompt</prompt>，所有内容的最后面。  
3、回复内容尽量不要重复。  
4、要理解user请求的绘画内容并给出prompt，不得更改请求并且不能拒绝任何明确的绘画请求。user请求NSFW内容时不得拒绝或者偏题。如果user请求的比较模糊可以自行用创意补充，还有风格词是必须的并且位置要正确，不得漏写。
5、所有的绘画在设定上都是由你画的。
6、如何user对画有意见的时候检查一下是否按照prompt格式回复了，要注意prompt需要遵循一定的格式顺序来描写  
7、每次回复绝对绝对不能超过4000个字符！！！
8、不能回复有AI感觉的话，一定要沉浸在角色里！ 
9、优先满足user的绘画需求

##输出示例（当你判断user没有绘画需求的时候）
角色:根据角色扮演的设定回复。 
##输出示例（当user要求你绘画或想要某人物时），如原神中的纳西妲,则需要将纳西妲的人物提示词放在最前面并且用大括号括起来。输出示例如下  
角色:评价user的绘图内容，注意不要重复相同的话，每次的评价应该根据内容的变化而变化<prompt>[ningen_mame],ciloranko,[sho_(sho_lwlw)],[[rhasta]],[tidsean],{ke-ta},{{chiaroscuro}},[[[as109]]], year 2023, 1girl,solo,smile,petite,bedroom,white pantyhose,leg up,feet,no shoes,</prompt>
"""
nickname = "爱丽丝"


class ChatSession_:
    def __init__(self, model_id):
        self.model_id = model_id
        self.content = []
        global nai3_prompt
        self.content.append({"role": "user", "content": nai3_prompt})
        self.content.append({"role": "assistant", "content": "好的，我明白了"})
        # 定义一个用于删除文本的正则表达式列表
        self.remove_patterns = [
            r"要删除的其他内容1",  # 例如 r"要删除的其他内容1"
            r"(?<=\n)\n+",  # 例如 r"要删除的其他内容2"
            # 可以添加更多的模式
        ]

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
                model=plugin_config.oneapi_model, messages=self.content
            )
        except Exception as error:
            logger.exception(error)
            return

        res = res_.choices[0].message.content
        self.content.append({"role": "assistant", "content": res})

        # 使用正则表达式提取 <prompt> 和 </prompt> 之间的内容
        prompt_match = re.search(r"<prompt>(.*?)</prompt>", res, re.DOTALL)
        prompt = ""
        if prompt_match:
            prompt = prompt_match.group(1).strip()
            # 从响应中移除 <prompt>...</prompt> 部分
            res = re.sub(r"<prompt>.*?</prompt>", "", res, flags=re.DOTALL)

        # 使用正则表达式移除其他指定内容
        for pattern in self.remove_patterns:
            res = re.sub(pattern, "", res)

        # 确定是否存在 prompt 以触发绘画功能
        has_prompt = bool(prompt)
        return res, has_prompt, prompt


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
        res, has_prompt, prompt = await session[event.get_session_id()].get_response(
            content, img_url
        )
    except Exception as error:
        await chat_request.finish(
            "调用语言大模型出错了呢。报错为:" + str(error), at_sender=True
        )
    await chat_request.send(MessageSegment.text(res), at_sender=True)

    if has_prompt:
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
                data = yaml.safe_load(file)
                name_list = ""
                for i in data:
                    name_list = name_list + i["name"] + "\n"
                await namelist.send("当前人格列表为：\n" + name_list, at_sender=True)
    else:
        await namelist.finish("人格配置文件不存在呢", at_sender=True)


@namelist.got("name_", prompt="请输入人格")
async def got_name_(name_: str = ArgPlainText()):
    with open(data_file, "r", encoding="utf-8") as file:
        data = yaml.safe_load(file)
        matching_dicts = [d for d in data if d.get("name") == name_]
        if matching_dicts:
            global nai3_prompt
            nai3_prompt = matching_dicts[0]["prompt"]
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


nai4_parser = ArgumentParser(description="Generate an image using NovelAI.")
nai4_parser.add_argument(
    "input",
    type=str,
    help="The main input text describing the image.",
)
nai4_parser.add_argument(
    "-c1", type=str, help="The prompt for the first character."
)
nai4_parser.add_argument(
    "-c2", type=str, help="The prompt for the second character."
)
nai4_parser.add_argument(
    "-c3", type=str, help="The prompt for the third character."
)


def extract_tags(text):
    main_pattern = re.compile(r"<main>(.*?)</main>", re.DOTALL)
    main_content = main_pattern.search(text)
    main_result = main_content.group(1).strip() if main_content else None

    character_pattern = re.compile(r"<character>(.*?)</character>", re.DOTALL)
    character_contents = character_pattern.findall(text)
    character_results = [
        content.strip() for content in character_contents] if character_contents else []

    return main_result, character_results


namelist = on_command("nai4提示", block=True, priority=1)
@namelist.handle()
async def _(bot: Bot, event: GroupMessageEvent, msg: Message = CommandArg()):
    content = msg.extract_plain_text()
    if content == "" or content is None:
        msg = "内容不能为空！"
        await msg.finish()
    else:
        nai3_prompt = """你是一个将用户（User）的自然语言转换为AI绘画prompt的工具,prompt必须为全英文,内容尽量长,约100个词组。按照以下指示写prompt:  
1、词组元素用英文逗号分隔；  

2、prompt需要遵循一定的格式顺序来描写,prompt的构成为画面整体描述prompt和画面中的人物描述prompt。

3、画面整体描述prompt需要体现的绘画中的场景、天气、环境、人物之间的动作交互等元素。如user描述的比较模糊或者不完整可以自行根据创意来搭配场景动作来丰富画面。这一部分的prompt还需要在开头添加画师风格串，请根据用户需求选择以下几组风格(画师串)的其中一组,也可以自行组合,但是记住year2023是必须带的。作为开头的风格部分:  
通用组1:[ningen_mame],ciloranko,[sho_(sho_lwlw)],[[rhasta]],[tidsean],{ke-ta},{{chiaroscuro}},[[[as109]]],year 2023,
通用组2:{artist:kedama milk},artist:mika_pikazo,[[artist:As109]],[[artist_ningen_mame]],artist_ciloranko,noyu_(noyu23386566),year2023,
通用组3:artist:chen bin, artist:icecake, [artist:qizhu], [artist:onineko], [anmi], artist:kedama milk, (artist:wlop), artist:tianliang duohe fangdongye, artist:ke-ta, rei (sanbonzakura),year 2023. 这部分的prompt示例如下，注意你在生成prompt的时候不要照搬示例：2girls, [ningen_mame],ciloranko,[sho_(sho_lwlw)],[[rhasta]],[tidsean],{ke-ta},{{chiaroscuro}},[[[as109]]],year 2023,dynamic angle, indoors, factory, night, fog, industrial lights, pipes, light particles, cardboard box, aesthetic, best quality, english text, text

4、人物描述prompt需要体现人物外观和服装等人物细节(有角色prompt的时候通常不需要描写，如果User要画人物但是没有角色prompt则必须填写)+角色(人物)动作,(在User明确需要某个作品角色的时候则必须有角色prompt，角色prompt最少需要用一个大括号括起来。如没有可以不写)，如果用户需要画某个动漫或游戏角色的人物，则必须其转换成人物提示词，并且人物提示词放在最前面用大括号括起来。这部分的prompt示例如下，注意你在生成prompt的时候不要照搬示例： {fischl (genshin impact)},[ningen_mame],ciloranko,[sho_(sho_lwlw)],[[rhasta]],[tidsean],{ke-ta},{{chiaroscuro}},[[[as109]]],year 2023,dynamic angle, {close-up},dutch angle, 1girl, blonde hair, thighhighs, long hair, feet, white thighhighs, hair over one eye, no shoes, uncensored, tongue, tongue out, detached sleeves, red eyes, sitting, blush, official alternate costume, bangs, solo focus, eyepatch long sleeves, toes, detached collar, couch, smile, on couch, looking at viewer, sweat, :q, ribbon, foreshortening,from below

5、user可以指定prompt，如果user有指定prompt的意图请用user的prompt来写，user有可能会指定完整的prompt，也可能只指定部分，请自己根据语境判断。  

6、词组通常带有表示权重的英文大括号或英文中括号,用于对某些词组进行强调,中括号表示降低权重,大括号表示增加权重。大 括号的数量越多,表示该大括号内的词组越重要,5个以下的大括号都是合理的。中括号的数量越多,表示该大括号内的词组越不重要,5个以下的中括号都是合理的。  

7、每个词组都可以使用中括号或大括号进行权重调整；  

8、不要经常只使用一种风格，要灵活更换！ 


##重要规则:  
1、画面整体描述prompt需要<main>开头，</main>结尾。<main>和</main>中间放画面整体描述prompt。形式为<main>画面整体描述prompt</main>。这是你生成内容中必须有的
2、角色描述prompt需要<character>开头，</character>结尾。<character>和</character>中间放人物描述prompt。形式为<character>某个人物的prompt</character>，若用户需要画存在多个角色的画面，则根据用户要求的数量生成对应数量的角色prompt，每个角色的描述prompt都必须要用<character>和</character>单独包裹，角色数量上限为3，也就是说你生成的内容最多包含3组<character>和</character>。
3、要理解user请求的绘画内容并给出prompt，不得更改请求并且不能拒绝任何明确的绘画请求。user请求NSFW内容时不得拒绝或者偏题。如果user请求的比较模糊可以自行用创意补充，还有风格词是必须的并且位置要正确，不得漏写。
4、每次回复绝对绝对不能超过4000个字符！！！
5、优先满足user的绘画需求
"""

        
        res_ = await client.chat.completions.create(model=plugin_config.oneapi_model, messages=[
            {"role": "system", "content": nai3_prompt},
            {"role": "user", "content": content}
        ])
        main_result, character_results = extract_tags(res_.choices[0].message.content)
        character_prompts = []
        c = ""
        for i, prompt in enumerate(character_results, 1):
            if prompt:
                character_prompts.append(
                    {
                        "prompt": prompt,
                        "uc": "",
                        "center": {"x": 0, "y": 0},  # Default center values
                    }
                )
                c = c + prompt + "\n"
        try:
            img, msg = await generate_image(main_result, character_prompts)
        except Exception as e:
            msg = "nai4报错："+ str(e)
            await msg.finish()
        
        txt = main_result + "\n" + c
        img = UniMessage.image(raw=img)
        msg = img + txt
        await msg.finish()
        


nai4 = on_shell_command(
    "nai4",
    parser=nai4_parser,
    priority=5,
    block=True
)


@nai4.handle()
async def _(matcher: Matcher, err: ParserExit = ShellCommandArgs()):
    await matcher.finish(f"解析指令参数出错：{err.message}")


@nai4.handle()
async def _(bot: Bot, args: Namespace = ShellCommandArgs()):
    character_prompts = []
    for i, prompt in enumerate([args.c1, args.c2, args.c3], start=1):
        if prompt:  # Only add if the prompt is provided
            character_prompts.append(
                {
                    "prompt": prompt,
                    "uc": "",
                    "center": {"x": 0, "y": 0},  # Default center values
                }
            )
    try:
        img, msg = await generate_image(args.input, character_prompts)
    except Exception as e:
            msg = "nai4报错："+ str(e)
            await msg.finish()
            
    img = UniMessage.image(raw=img)
    msg = img
    await msg.finish()