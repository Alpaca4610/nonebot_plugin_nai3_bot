<div align="center">
  <a href="https://v2.nonebot.dev/store"><img src="https://github.com/A-kirami/nonebot-plugin-template/blob/resources/nbp_logo.png" width="180" height="180" alt="NoneBotPluginLogo"></a>
  <br>
  <p><img src="https://github.com/A-kirami/nonebot-plugin-template/blob/resources/NoneBotPlugin.svg" width="240" alt="NoneBotPluginText"></p>
</div>

<div align="center">

# nonebot-plugin-nai3-bot
</div>

# 介绍
- 本插件基于GPT4+NovelAI V3,Bot在将自然语言转换为NAI3提示词并绘图发送的同时以自定义人格与用户聊天。
- 用户可以正常与指定人格（需要调教prompt,目前插件内置的人格为群友指定的BA角色天童爱丽丝）聊天。在聊天过程中可以使用自然语言描述AI绘图的需求,Bot会根据用户的聊天内容修改AI绘图所用的提示词（见效果图）,并且判断是否需要调用Novel V3模型进行绘画。如果为正常聊天则不会触发绘画功能,如果Bot判断用户有AI绘画的需求,则会调用NAI3绘图,并将图片和提示词发送到群内。
- 每个用户和Bot有独立的聊天记录。

# 效果
![Alt](demo1.jpeg)

# 安装
* 手动安装
  ```
  git clone https://github.com/Alpaca4610/nonebot_plugin_nai3_bot.git
  ```

  下载完成后在bot项目的pyproject.toml文件手动添加插件：

  ```
  plugin_dirs = ["xxxxxx","xxxxxx",......,"下载完成的插件路径/nonebot-plugin-nai3-bot"]
  ```
* 使用 pip
  ```
  pip install nonebot-plugin-nai3-bot
  ```
# 配置文件

在Bot根目录下的.env文件中追加如下内容：

必填内容：
```
nai3_token = "xxxx"  # （必填）NovelAI的token
oneapi_key = "sk-xxxxxxxxxx"  # （必填）OpenAI官方或者是支持OneAPI的大模型中转服务商提供的KEY
```

可选内容：
```
oneapi_url = "https://xxxxxxxxx"  # （可选）大模型中转服务商提供的中转地址,使用OpenAI官方服务不需要填写
oneapi_model = "gpt-4" # （可选）使用的语言大模型,建议使用gpt4或gpt4o模型以达到更好的体验效果此项,默认使用gpt-4模型
```
NAI3的token获取地址方法：
![Alt](image.png)

# 使用方法
- **  聊天内容/绘图需求      （**是触发与Bot对话的关键字）
- 记忆清除 清除当前用户的聊天记录

# 可能存在的问题
- 由于调教prompt的原因，机器人可能会偶尔出错，此时继续和TA对话或者是使用记忆清除命令重新开始对话即可。
- 注意语言大模型的token消耗量
- 插件目前没有实现绘图排队提醒，多用户同时绘图NAI3可能会返回错误。

# TODO
- [ ] 添加用户自定义人格功能
- [ ] 代理支持
- [ ] 支持绘图排队信息提醒(NAI3只支持一次出一张图)
