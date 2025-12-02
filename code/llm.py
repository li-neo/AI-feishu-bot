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


def llm_request(user_input, image_inputs=None, previous_response_id=None):
    """调用LLM API并返回响应内容，使用Responses API的session缓存
    
    Args:
        user_input: 用户输入的内容（纯文本）
        image_inputs: 图片输入列表，可以是URL或base64编码的图片数据（可选）
        previous_response_id: 上一次请求的ID，用于上下文管理
        
    Returns:
        tuple: (str, str) - AI模型生成的回复内容和当前请求的ID，如果出错则返回(None, None)
    """
    client = create_ark_client()
    try:
        # 构建输入消息
        input_messages = []
        
        # 对于首次请求，添加系统提示
        if not previous_response_id:
            input_messages.append({
                "role": "system",
                "content": ARK_SYSTEM_PROMPT
            })
        
        if image_inputs:
            # 构建多模态输入
            # 参考官方示例：当同时有图片和文本时，content应该是一个列表
            # 包含input_text和input_image类型的对象
            user_content = []
            
            # 添加文本内容（如果有）
            if user_input:
                user_content.append({
                    "type": "input_text",
                    "text": user_input
                })
            
            # 添加图片内容
            for image_data in image_inputs:
                # 检查是否为base64编码的图片（以"data:"开头）
                if image_data.startswith("data:"):
                    # 对于base64编码的图片，使用input_image类型和image_url字段
                    user_content.append({
                        "type": "input_image",
                        "image_url": image_data
                    })
                else:
                    # 对于URL形式的图片，同样使用input_image类型和image_url字段
                    user_content.append({
                        "type": "input_image",
                        "image_url": {
                            "url": image_data
                        }
                    })
            
            # 添加用户输入（多模态）
            input_messages.append({
                "role": "user",
                "content": user_content
            })
        else:
            # 添加纯文本用户输入
            input_messages.append({
                "role": "user",
                "content": user_input
            })
        
        # 调用模型API，使用Responses API
        response = client.responses.create(
            model=ARK_MODEL,  # 从配置文件读取模型ID
            max_output_tokens=ARK_MAX_TOKENS,  # 从配置文件读取最大生成长度
            temperature=ARK_TEMPERATURE,  # 从配置文件读取温度参数
            top_p=ARK_TOP_P,  # 从配置文件读取核采样参数
            #reasoning=ARK_REASONING_EFFORT,  # 从配置文件读取推理努力程度，使用正确的对象格式
            input=input_messages,  # 输入消息
            previous_response_id=previous_response_id,  # 上一次请求的ID，用于上下文管理
            caching={"type": "enabled"},
            thinking={"type": "disabled"}
        )
        
        # 解析模型生成的内容
        ai_content = ""
        response_message = response.output[0]
        
        # 遍历content列表，处理不同类型的内容
        for content_item in response_message.content:
            # 处理文本类型
            if hasattr(content_item, 'type') and content_item.type == 'output_text':
                if hasattr(content_item, 'text'):
                    ai_content += content_item.text
            # 处理图片类型（如果有）
            elif hasattr(content_item, 'type') and content_item.type == 'output_image':
                if hasattr(content_item, 'url'):
                    # 图片类型可以根据需要进行处理，这里简单拼接URL
                    ai_content += f"\n[图片: {content_item.url}]"
            # 可以添加其他类型的处理
        
        # 返回模型生成的内容和当前请求的ID
        return ai_content, response.id
    except Exception as e:
        # 异常处理
        print(f"API调用出错: {e}")
        return None, None


