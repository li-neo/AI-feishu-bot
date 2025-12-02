#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
消息模块
用于处理飞书消息相关的功能
"""

import os
import json
import requests
import sys
import time
from typing import Dict, Any, List, Optional, Set

import lark_oapi as lark
from lark_oapi.api.im.v1 import *
from config import PROCESSED_MESSAGES_FILE, MAX_MESSAGE_AGE, APP_ID, APP_SECRET

# 用于消息去重的集合，存储已处理的消息ID
processed_messages: Set[str] = set()

def load_processed_messages() -> None:
    """
    从持久化文件加载已处理的消息ID
    """
    global processed_messages
    if os.path.exists(PROCESSED_MESSAGES_FILE):
        try:
            with open(PROCESSED_MESSAGES_FILE, "r") as f:
                for line in f:
                    msg_id = line.strip()
                    if msg_id:
                        processed_messages.add(msg_id)
            print(f"Loaded {len(processed_messages)} processed messages from file")
        except Exception as e:
            print(f"ERROR: Loading processed messages: {e}", file=sys.stderr)

def save_processed_message(message_id: str) -> None:
    """
    将已处理的消息ID保存到持久化文件
    
    Args:
        message_id: 消息ID
    """
    try:
        with open(PROCESSED_MESSAGES_FILE, "a") as f:
            f.write(f"{message_id}\n")
    except Exception as e:
        print(f"ERROR: Saving processed message: {e}", file=sys.stderr)

def is_message_valid(message_id: str, message_time: int) -> bool:
    """
    检查消息是否有效（未被处理过且在有效期内）
    
    Args:
        message_id: 消息ID
        message_time: 消息时间戳（秒）
        
    Returns:
        bool: 消息是否有效
    """
    # 检查消息是否已经被处理过
    if message_id in processed_messages:
        print(f"INFO: Message {message_id} already processed, ignoring")
        return False
    
    # 获取当前时间戳（秒）
    current_time = int(time.time())
    
    # 计算消息年龄
    message_age = current_time - message_time
    
    # 只处理5分钟内的消息，避免处理历史消息
    if message_age > MAX_MESSAGE_AGE:
        print(f"INFO: Message {message_id} is too old ({message_age}s > {MAX_MESSAGE_AGE}s), ignoring")
        return False
    
    return True

def mark_message_processed(message_id: str) -> None:
    """
    标记消息为已处理
    
    Args:
        message_id: 消息ID
    """
    processed_messages.add(message_id)
    save_processed_message(message_id)

def send_message_to_chat(tenant_access_token: str, chat_id: str, content: str, msg_type: str = "text") -> Dict[str, Any]:
    """
    向指定群组发送消息

    Args:
        tenant_access_token: 租户访问令牌
        chat_id: 群组ID
        content: 消息内容
        msg_type: 消息类型

    Returns:
        Dict[str, Any]: 发送结果
    """
    url = "https://open.feishu.cn/open-apis/im/v1/messages"
    headers = {
        "Authorization": f"Bearer {tenant_access_token}",
        "Content-Type": "application/json; charset=utf-8"
    }
    params = {
        "receive_id_type": "chat_id"
    }
    
    # 构造消息内容
    if msg_type == "text":
        msg_content = {"text": content}
    else:
        msg_content = json.loads(content) if isinstance(content, str) and content.startswith('{') else content
    
    # 飞书API要求content字段是JSON字符串
    payload = {
        "receive_id": chat_id,
        "msg_type": msg_type,
        "content": json.dumps(msg_content)
    }
    
    try:
        print(f"POST: {url} with params: {params}")
        print(f"Request payload: {json.dumps(payload)}")
        response = requests.post(url, headers=headers, params=params, json=payload)
        response.raise_for_status()
        
        result = response.json()
        print(f"Response: {json.dumps(result)}")
        
        if result.get("code", 0) != 0:
            error_msg = f"failed to send message: {result.get('msg', 'unknown error')}"
            print(f"ERROR: {error_msg}", file=sys.stderr)
            raise Exception(error_msg)
            
        return result
        
    except Exception as e:
        error_msg = f"Error sending message: {e}"
        if hasattr(e, 'response') and e.response is not None:
            error_msg += f" Response: {e.response.text}"
        print(f"ERROR: {error_msg}", file=sys.stderr)
        raise

def get_image_base64(tenant_access_token: str, message_id: str, image_key: str) -> Optional[str]:
    """
    根据消息ID和图片key获取图片二进制流，并转换为base64编码

    Args:
        tenant_access_token: 租户访问令牌
        message_id: 消息ID
        image_key: 图片key

    Returns:
        Optional[str]: 图片的base64编码字符串，如果获取失败则返回None
    """
    import base64
    
    try:
        # 创建飞书SDK客户端
        client = lark.Client.builder() \
            .app_id(APP_ID) \
            .app_secret(APP_SECRET) \
            .log_level(lark.LogLevel.DEBUG) \
            .build()
        
        # 构造请求对象
        request: GetMessageResourceRequest = GetMessageResourceRequest.builder() \
            .message_id(message_id) \
            .file_key(image_key) \
            .type("image") \
            .build()
        
        # 发起请求
        response: GetMessageResourceResponse = client.im.v1.message_resource.get(request)
        
        # 处理失败返回
        if not response.success():
            error_msg = f"client.im.v1.message_resource.get failed, code: {response.code}, msg: {response.msg}, log_id: {response.get_log_id()}"
            if hasattr(response, 'raw') and response.raw:
                error_msg += f", resp: {json.dumps(json.loads(response.raw.content), indent=4, ensure_ascii=False)}"
            print(f"ERROR: {error_msg}", file=sys.stderr)
            return None
        
        # 读取图片二进制数据
        image_data = response.file.read()
        
        # 获取Content-Type（默认为image/jpeg）
        content_type = "image/jpeg"
        
        # 将二进制数据转换为base64编码
        base64_encoded = base64.b64encode(image_data).decode('utf-8')
        
        # 返回带前缀的base64字符串，方便LLM处理
        return f"data:{content_type};base64,{base64_encoded}"
            
    except Exception as e:
        error_msg = f"Error getting image data with SDK: {e}"
        print(f"ERROR: {error_msg}", file=sys.stderr)
        return None


def reply_message(tenant_access_token: str, message_id: str, content: str, msg_type: str = "text") -> Dict[str, Any]:
    """
    回复指定消息

    Args:
        tenant_access_token: 租户访问令牌
        message_id: 消息ID
        content: 回复内容
        msg_type: 消息类型

    Returns:
        Dict[str, Any]: 回复结果
    """
    url = f"https://open.feishu.cn/open-apis/im/v1/messages/{message_id}/reply"
    headers = {
        "Authorization": f"Bearer {tenant_access_token}",
        "Content-Type": "application/json; charset=utf-8"
    }
    
    # 构造消息内容
    if msg_type == "text":
        msg_content = {"text": content}
    else:
        msg_content = json.loads(content) if isinstance(content, str) and content.startswith('{') else content
    
    payload = {
        "content": json.dumps(msg_content) if isinstance(msg_content, dict) else msg_content,
        "msg_type": msg_type
    }
    
    try:
        print(f"POST: {url}")
        print(f"Request payload: {json.dumps(payload)}")
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        
        result = response.json()
        print(f"Response: {json.dumps(result)}")
        
        if result.get("code", 0) != 0:
            error_msg = f"failed to reply message: {result.get('msg', 'unknown error')}"
            print(f"ERROR: {error_msg}", file=sys.stderr)
            raise Exception(error_msg)
            
        return result
        
    except Exception as e:
        error_msg = f"Error replying message: {e}"
        if hasattr(e, 'response') and e.response is not None:
            error_msg += f" Response: {e.response.text}"
        print(f"ERROR: {error_msg}", file=sys.stderr)
        raise

# 初始化时加载已处理的消息ID
load_processed_messages()