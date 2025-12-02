#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
事件处理模块
用于处理飞书事件订阅，包括消息接收事件
"""

import json
import sys
import time
from typing import Dict, Any

import lark_oapi as lark
from lark_oapi.api.im.v1 import *

from auth import get_tenant_access_token
from message import is_message_valid, mark_message_processed
from llm import llm_request
from config import BOT_NAME

def call_ai_model(query: str) -> str:
    """
    调用大模型处理查询
    
    Args:
        query: 用户查询内容
        
    Returns:
        str: 大模型返回的回复内容
    """
    messa = llm_request(query)
    return f"{messa}"

def do_p2_im_message_receive_v1(data: P2ImMessageReceiveV1) -> None:
    """
    处理接收消息事件
    
    Args:
        data: 接收消息事件数据
    """
    print(f'[do_p2_im_message_receive_v1 access], data: {lark.JSON.marshal(data, indent=4)}')
    
    try:
        from config import APP_ID, APP_SECRET
        
        # 获取 tenant_access_token
        tenant_access_token, err = get_tenant_access_token(APP_ID, APP_SECRET)
        if err:
            print(f"ERROR: getting tenant_access_token: {err}", file=sys.stderr)
            return
        
        event = data.event
        if not event or not event.message:
            print("ERROR: Invalid event data", file=sys.stderr)
            return
            
        message = event.message
        
        # 检查事件类型，只处理消息创建事件
        event_type = data.header.event_type if hasattr(data.header, 'event_type') else ''
        if event_type != 'im.message.receive_v1':
            print(f"INFO: Ignoring non-message event: {event_type}")
            return
        
        # 获取消息时间戳
        message_time = 0
        if hasattr(event, 'timestamp') and event.timestamp:
            # 飞书事件的timestamp通常是毫秒级，转换为秒
            message_time = int(event.timestamp) // 1000
        elif hasattr(message, 'create_time') and message.create_time:
            # 消息的create_time通常是秒级
            message_time = int(message.create_time)
        
        # 检查消息是否有效
        if not is_message_valid(message.message_id, message_time):
            # 如果消息无效但未被标记为已处理，则标记为已处理
            mark_message_processed(message.message_id)
            return
        
        # 只处理群聊中的@消息
        if message.chat_type != "group":
            print("INFO: Not a group message, ignoring")
            # 标记为已处理
            mark_message_processed(message.message_id)
            return

        # 提取消息内容
        content = json.loads(message.content) if message.content else {}
        text_content = content.get("text", "") if isinstance(content, dict) else str(content)
            




        
        if not message.mentions and BOT_NAME not in text_content:
            print("INFO: No mentions in message, ignoring")
            # 标记为已处理
            mark_message_processed(message.message_id)
            return
        
            

        
        # 检查是否有@当前机器人或文本中包含BOT_NAME
        bot_mentioned = False

        if message.mentions:
            for mention in message.mentions:
                # 检查是否@了当前机器人
                if mention.name == BOT_NAME:
                    bot_mentioned = True
                    break
        # 如果没有@提及，检查文本中是否包含BOT_NAME
        elif BOT_NAME in text_content:
            bot_mentioned = True
        
        # 如果没有@机器人且文本中也不包含BOT_NAME，直接返回
        if not bot_mentioned:
            print("INFO: Bot not mentioned in message and BOT_NAME not in text, ignoring")
            # 标记为已处理
            mark_message_processed(message.message_id)
            return
                
        # 清理@标记，只保留问题文本
        query_text = text_content
        if isinstance(content, dict) and "text" in content and message.mentions:
            # 移除@标记
            for mention in message.mentions:
                if mention.key:
                    query_text = query_text.replace(mention.key, "").strip()
        
        # 检查处理后的文本是否为空
        if not query_text:
            print("INFO: Empty query after removing mentions, ignoring")
            # 标记为已处理
            mark_message_processed(message.message_id)
            return
        
        print(f"Processing query: {query_text}")
        
        # 调用大模型处理
        ai_response = call_ai_model(query_text)
        
        # 回复消息
        from message import reply_message
        reply_result = reply_message(
            tenant_access_token=tenant_access_token,
            message_id=message.message_id,
            content=ai_response,
            msg_type="text"
        )
        
        print(f"Reply sent successfully: {json.dumps(reply_result)}")
        
        # 标记消息为已处理
        mark_message_processed(message.message_id)
        
    except Exception as e:
        print(f"ERROR: processing message event: {e}", file=sys.stderr)