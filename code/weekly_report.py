#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
周报模块
用于处理飞书周报相关的功能
"""

import json
import sys
import time
import copy
from typing import Optional, List, Dict, Any

from auth import get_tenant_access_token
from chat import get_bot_chats
from message import send_message_to_chat
from card import CARD_CONFIG



def create_weekly_report_card(report_content: Any) -> Dict[str, Any]:
    """
    创建周报飞书卡片
    
    Args:
        report_content: 周报内容（兼容旧接口，实际不再使用）
        
    Returns:
        Dict[str, Any]: 飞书卡片JSON结构
    """
    # 重新加载card模块以获取最新的卡片数据
    import importlib
    from card import get_card_data, CARD_TEMPLATE_ID, CARD_TEMPLATE_VERSION
    importlib.reload(sys.modules['card'])
    
    # 重新获取卡片数据
    card_data = get_card_data()
    
    # 构建新的卡片配置
    return {
        "template_id": CARD_TEMPLATE_ID,
        "template_version_name": CARD_TEMPLATE_VERSION,
        "template_variable": {
            "common": card_data["common"], 
            "item": card_data["items"]
        }
    }



def send_weekly_report_to_groups(report_content: str, target_chat_ids: Optional[List[str]] = None, use_card: bool = True) -> List[Dict[str, Any]]:
    """
    向指定群组发送AI周报
    
    Args:
        report_content: 周报内容
        target_chat_ids: 目标群组ID列表，如果为None则发送给所有机器人所在的群组
        use_card: 是否使用飞书卡片格式发送
        
    Returns:
        List[Dict[str, Any]]: 发送结果列表
    """
    results = []
    
    try:
        from config import APP_ID, APP_SECRET
        
        # 获取 tenant_access_token
        tenant_access_token, err = get_tenant_access_token(APP_ID, APP_SECRET)
        if err:
            raise Exception(f"getting tenant_access_token: {err}")
        
        # 如果没有指定目标群组，则获取机器人所在的所有群组
        if target_chat_ids is None:
            chats = get_bot_chats(tenant_access_token)
            target_chat_ids = [chat["chat_id"] for chat in chats if chat.get("chat_id")]
        
        print(f"Sending weekly report to {len(target_chat_ids)} groups: {target_chat_ids}")
        
        # 向每个群组发送周报
        for chat_id in target_chat_ids:
            try:
                if use_card:
                    # 使用飞书卡片格式发送
                    # create_weekly_report_card 现在会自动处理 report_content 是字符串还是结构化数据的情况
                    card = create_weekly_report_card(report_content)
                    # 飞书卡片消息要求content是包含type和data字段的对象
                    card_content = {
                        "type": "template",
                        "data": card
                    }
                    result = send_message_to_chat(
                        tenant_access_token=tenant_access_token,
                        chat_id=chat_id,
                        content=card_content,
                        msg_type="interactive"
                    )
                else:
                    # 使用文本格式发送
                    # 如果 report_content 是 list/dict，需要先转为字符串
                    content_to_send = report_content
                    if not isinstance(report_content, str):
                        content_to_send = json.dumps(report_content, ensure_ascii=False, indent=2)
                        
                    result = send_message_to_chat(
                        tenant_access_token=tenant_access_token,
                        chat_id=chat_id,
                        content=content_to_send,
                        msg_type="text"
                    )
                results.append({
                    "chat_id": chat_id,
                    "success": True,
                    "result": result
                })
                print(f"Successfully sent report to chat {chat_id}")
            except Exception as e:
                results.append({
                    "chat_id": chat_id,
                    "success": False,
                    "error": str(e)
                })
                print(f"Failed to send report to chat {chat_id}: {e}", file=sys.stderr)
                
    except Exception as e:
        print(f"ERROR: sending weekly report: {e}", file=sys.stderr)
        raise
        
    return results
