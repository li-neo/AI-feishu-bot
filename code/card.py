#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Card 模板
"""

import json
import sys
from typing import Dict, Any, List, Optional
from doc_fetcher import get_weekly_report_data
from config import (
    SPREADSHEET_TOKEN, SHEET_ID, DOC_TOKEN,
    BITABLE_TOKEN, TABLE_ID, ENABLE_DYNAMIC_DATA,
    _STATIC_COMMON, _STATIC_ITEMS,
    CARD_TEMPLATE_ID, CARD_TEMPLATE_VERSION
)


def get_card_data() -> Dict[str, Any]:
    """
    获取卡片数据
    
    Returns:
        Dict[str, Any]: 包含common和items的卡片数据
    """
    print(f"DEBUG: ENABLE_DYNAMIC_DATA: {ENABLE_DYNAMIC_DATA}")
    if ENABLE_DYNAMIC_DATA:
        try:
            # 从飞书文档、表格或多维表格动态获取数据
            print(f"DEBUG: Getting dynamic data...")
            data = get_weekly_report_data(
                doc_token=DOC_TOKEN if DOC_TOKEN else None,
                spreadsheet_token=SPREADSHEET_TOKEN if SPREADSHEET_TOKEN else None,
                sheet_id=SHEET_ID if SHEET_ID else None,
                bitable_token=BITABLE_TOKEN if BITABLE_TOKEN else None,
                table_id=TABLE_ID if TABLE_ID else None
            )
            print(f"DEBUG: Dynamic data received: {json.dumps(data, ensure_ascii=False)}")
            
            # 优化：检查每个item的pictures字段，如果为空，则添加默认图片
            for item in data["items"]:
                if not item.get("pictures") or len(item["pictures"]) == 0:
                    # 添加默认图片或从静态数据中获取图片
                    default_pics = [
                        {"img_key": "img_v3_02ad_e19fca1f-912a-450e-95de-3c229091b53g"}  # 示例默认图片
                    ]
                    item["pictures"] = default_pics
                    print(f"DEBUG: Added default pictures to item: {item['name']}")
            
            return data
        except Exception as e:
            print(f"WARNING: Failed to get dynamic data, using static data instead: {e}", file=sys.stderr)
            # 如果动态获取失败，回退到静态数据
            return {
                "common": _STATIC_COMMON,
                "items": _STATIC_ITEMS
            }
    else:
        # 使用静态数据
        print(f"DEBUG: Using static data")
        return {
            "common": _STATIC_COMMON,
            "items": _STATIC_ITEMS
        }

# 获取卡片数据
card_data = get_card_data()

# 卡片消息配置
CARD_CONFIG = {
    "template_id": CARD_TEMPLATE_ID,  # 卡片ID，从卡片搭建工具中获取
    "template_version_name": CARD_TEMPLATE_VERSION,
    "template_variable": {
        "common": card_data["common"], 
        "item": card_data["items"]
    }
}