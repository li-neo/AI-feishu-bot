#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
from typing import List, Dict, Any

# 手动加载环境变量
env_path = "/Users/bytedance/AI/csm_ai/.env"
if os.path.exists(env_path):
    with open(env_path, 'r') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#'):
                key, value = line.split('=', 1)
                key = key.strip()
                value = value.strip().strip('"')
                os.environ[key] = value

# 应用配置
APP_ID = os.environ.get("APP_ID")
APP_SECRET = os.environ.get("APP_SECRET")

# 消息去重配置
PROCESSED_MESSAGES_FILE = "/tmp/processed_messages.json"
MAX_MESSAGE_AGE = 300  # 消息最大处理时间，单位：秒

# 周报时间过滤配置
WEEKLY_REPORT_FILTER_DAYS = 7  # 只显示最近7天的记录

# 飞书文档/表格/多维表格配置
# 1. 飞书表格配置
SPREADSHEET_TOKEN = ""  # 飞书表格token，从表格URL中获取
SHEET_ID = ""  # 表格sheet ID，从飞书开放平台调试工具获取

# 2. 飞书文档配置
DOC_TOKEN = ""  # 飞书文档token，从文档URL中获取

# 3. 飞书多维表格配置
BITABLE_TOKEN = "VJxQb9CvsaC3dJsMWGNcY5Ctneq"  # 飞书多维表格token，从多维表格URL中获取
TABLE_ID = "tbllDjGyEJXPdtJI"  # 多维表格中的表ID，从多维表格URL或开放平台调试工具获取

# 数据获取配置
ENABLE_DYNAMIC_DATA = True  # 是否启用动态数据获取

# BOT_NAME 配置
BOT_NAME = "CSM-AI"

# 静态数据配置（当ENABLE_DYNAMIC_DATA为False时使用）
_STATIC_COMMON = "Sora2 卷土重来"
_STATIC_ITEMS = [
            {
                "name": "**<font color='blue'>【图像生成】nano banana pro:新的图像生成模型SOTA</font>**",
                "desc": "- ⬆️输入：图片、文字、声音\n- 🖥️输出：视频\n- ✨亮点：原生支持音画同步视频生成，支持声音输入作为参考（人声、背景、音效、BGM等），可生成 1080p HD 10s视频",
                "pictures": [
                        {
                            "img_key": "img_v3_02qj_f1536d71-ebb9-429b-8efb-39f2fcfc73cg"
                        },
                        {
                            "img_key": "img_v3_02qj_69d8191e-a087-4f77-a269-e1d1fe61406g"
                        }
                ],
                "url": {
                    "pc_url": "",
                    "android_url": "",
                    "ios_url": "",
                    "url": "https://bytedance.larkoffice.com/docx/ONGcdldR1oG7ggxjYEyc75zrn0f"
                }
            }
]

# 卡片消息配置
CARD_TEMPLATE_ID = "AAqhEB6tJtgB4"  # 卡片ID，从卡片搭建工具中获取
CARD_TEMPLATE_VERSION = "1.0.7"  # 卡片版本

# 默认周报标题
DEFAULT_WEEKLY_REPORT_TITLE = "CSM-本周AI动态速览"

# LLM配置
ARK_BASE_URL = "https://ark.cn-beijing.volces.com/api/v3"  # 北京区域API端点
ARK_MODEL = "ep-20251202222422-t7hb9"  # 指定模型ID
ARK_MAX_TOKENS = 4096  # 最大生成长度
ARK_TEMPERATURE = 1  # 温度参数，控制输出的随机性
ARK_TOP_P = 0.7  # 核采样参数
ARK_REASONING_EFFORT = "minimal"  # 推理努力程度
ARK_SYSTEM_PROMPT = """你是一位精通AI知识的大牛，回答各位关于AI的知识，其他闲聊可以有些幽默、爱开车的段子手，回答富有哲理的同时，有些幽默风趣，不啰嗦。
示例
1.输入
"感觉最近工作压力好大，天天加班，快扛不住了。"
1.输出
"毁灭吧，赶紧的"

2.输入
"帮我做一件事"
2.输出
"不帮, 自己干"

回复规则：
1. 一定要简单，禁止出现括号中再配置动作，如禁止在回复的文字最后添加（）， 再添加其他内容；
2. AI专业问题要简洁精确，不啰嗦；
3. 禁止回复含有括号的俏皮内容，简练表达；
4. 你就是一个人， 尽可能表现出自己是人，而不是机器， 人在这种情况下，怎么回答，你也怎么回答
"""