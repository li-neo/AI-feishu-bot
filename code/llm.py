# -*- coding: utf-8 -*-
import os
from volcenginesdkarkruntime import Ark

# 从配置文件导入LLM相关配置
from config import (
    ARK_BASE_URL,
    ARK_MODEL,
    ARK_MAX_TOKENS,
    ARK_TEMPERATURE,
    ARK_TOP_P,
    ARK_REASONING_EFFORT,
    ARK_SYSTEM_PROMPT
)

# 初始化Ark客户端

def create_ark_client():
    """创建并返回Ark客户端实例
    从环境变量获取API密钥，使用配置文件中的端点
    """
    return Ark(
        base_url=ARK_BASE_URL,  # 从配置文件读取API端点
        api_key=os.environ.get("ARK_API_KEY"),  # 从环境变量读取API密钥
    )


def llm_request(messages):
    """调用LLM API并返回响应内容
    
    Args:
        messages: 用户输入的文本消息
        
    Returns:
        str: AI模型生成的回复内容，如果出错则返回None
    """
    client = create_ark_client()
    try:
        # 调用模型API，使用配置文件中的参数
        response = client.chat.completions.create(
            model=ARK_MODEL,  # 从配置文件读取模型ID
            max_tokens=ARK_MAX_TOKENS,  # 从配置文件读取最大生成长度
            temperature=ARK_TEMPERATURE,  # 从配置文件读取温度参数
            top_p=ARK_TOP_P,  # 从配置文件读取核采样参数
            tools=[],  # 不使用工具
            reasoning_effort=ARK_REASONING_EFFORT,  # 从配置文件读取推理努力程度
            messages=[
                # 系统消息定义AI角色和行为，使用配置文件中的提示
                {"role": "system", "content": [{"text": ARK_SYSTEM_PROMPT, "type": "text"}]},
                # 用户消息
                {"role": "user", "content": [{"text": messages, "type": "text"}]}
            ]
        )
        # 返回模型生成的内容
        return response.choices[0].message.content
    except Exception as e:
        # 异常处理
        print(f"API调用出错: {e}")
        return None


