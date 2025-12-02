#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
群组模块
用于处理飞书群组相关的功能
"""

import json
import requests
import sys
from typing import List, Dict, Any

def get_bot_chats(tenant_access_token: str, page_size: int = 100) -> List[Dict[str, Any]]:
    """
    获取机器人所在的群列表

    Args:
        tenant_access_token: 租户访问令牌
        page_size: 分页大小

    Returns:
        List[Dict[str, Any]]: 群组列表
    """
    url = "https://open.feishu.cn/open-apis/im/v1/chats"
    headers = {
        "Authorization": f"Bearer {tenant_access_token}",
        "Content-Type": "application/json; charset=utf-8"
    }
    
    all_chats = []
    page_token = ""
    
    while True:
        params = {
            "page_size": page_size
        }
        if page_token:
            params["page_token"] = page_token
            
        try:
            print(f"GET: {url} with params: {params}")
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()
            
            result = response.json()
            print(f"Response: {json.dumps(result)}")
            
            if result.get("code", 0) != 0:
                error_msg = f"failed to get bot chats: {result.get('msg', 'unknown error')}"
                print(f"ERROR: {error_msg}", file=sys.stderr)
                raise Exception(error_msg)
                
            data = result.get("data", {})
            items = data.get("items", [])
            all_chats.extend(items)
            
            if not data.get("has_more", False):
                break
            page_token = data.get("page_token", "")
            
        except Exception as e:
            error_msg = f"Error getting bot chats: {e}"
            if hasattr(e, 'response') and e.response is not None:
                error_msg += f" Response: {e.response.text}"
            print(f"ERROR: {error_msg}", file=sys.stderr)
            raise
    
    return all_chats