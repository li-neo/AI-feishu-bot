#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
认证模块
用于处理飞书API的认证功能
"""

import json
import requests
import sys
from typing import Tuple, Optional

from config import APP_ID, APP_SECRET

def get_tenant_access_token(app_id: Optional[str] = None, app_secret: Optional[str] = None) -> Tuple[str, Exception]:
    """
    获取 tenant_access_token

    Args:
        app_id: 应用ID，如果为None则使用配置文件中的APP_ID
        app_secret: 应用密钥，如果为None则使用配置文件中的APP_SECRET

    Returns:
        Tuple[str, Exception]: (access_token, error)
    """
    # 使用传入的参数或配置文件中的值
    app_id = app_id or APP_ID
    app_secret = app_secret or APP_SECRET
    
    # 验证参数
    if not app_id or not app_secret:
        error_msg = "app_id or app_secret is null"
        print(f"ERROR: {error_msg}", file=sys.stderr)
        return "", Exception(error_msg)
    
    url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
    payload = {
        "app_id": app_id,
        "app_secret": app_secret
    }
    headers = {
        "Content-Type": "application/json; charset=utf-8"
    }
    
    try:
        print(f"POST: {url}")
        print(f"Request payload: {json.dumps(payload)}")
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()

        result = response.json()
        print(f"Response: {json.dumps(result)}")

        if result.get("code", 0) != 0:
            error_msg = f"failed to get tenant_access_token: {result.get('msg', 'unknown error')}"
            print(f"ERROR: {error_msg}", file=sys.stderr)
            return "", Exception(error_msg)

        return result["tenant_access_token"], None

    except Exception as e:
        error_msg = f"Error getting tenant_access_token: {e}"
        if hasattr(e, 'response') and e.response is not None:
            error_msg += f" Response: {e.response.text}"
        print(f"ERROR: {error_msg}", file=sys.stderr)
        return "", e