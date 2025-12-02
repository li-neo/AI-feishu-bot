#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试周报卡片生成和推送功能
"""

import os
from weekly_report import create_weekly_report_card, send_weekly_report_to_groups

# 从环境变量获取测试群组ID
TEST_CHAT_ID = os.environ.get("TEST_CHAT_ID", "")
def test_create_and_send_weekly_report():
    """测试创建并推送周报卡片 - 直接使用CARD_CONFIG中的模拟数据"""
    # 1. 测试创建卡片
    print("=== 测试创建卡片 ===")
    
    # 重新加载card模块以获取最新的卡片数据
    import importlib
    import card
    importlib.reload(card)
    
    # 直接查看card_data以了解数据结构
    print(f"DEBUG: card_data: {card.card_data}")
    
    # 重新获取卡片
    card_obj = create_weekly_report_card(None)
    
    # 验证卡片生成结果
    print("Card generated successfully!")
    print(f"Card type: {type(card_obj)}")
    print(f"Card keys: {list(card_obj.keys())}")
    
    # 验证template_variable
    template_var = card_obj.get('template_variable', {})
    print(f"Template variable keys: {list(template_var.keys())}")
    print(f"Common value: {template_var.get('common')}")
    
    # 验证item字段 - 现在是字符串占位符
    items = template_var.get('item')
    print(f"Items type: {type(items)}")
    print(f"Items value: {items}")
    
    # 查看静态数据
    from config import _STATIC_ITEMS
    print(f"DEBUG: _STATIC_ITEMS: {_STATIC_ITEMS}")
    
    # 2. 测试推送卡片
    print("\n=== 测试推送卡片 ===")
    try:
        # 调用推送函数，使用TEST_CHAT_ID进行测试
        results = send_weekly_report_to_groups(
            report_content=None,  # 兼容旧接口，实际不再使用
            target_chat_ids=[TEST_CHAT_ID] if TEST_CHAT_ID else None,  # 使用测试群组ID
            use_card=True  # 使用卡片格式发送
        )
        
        # 打印推送结果
        print(f"\n推送结果:")
        print(f"总发送数量: {len(results)}")
        success_count = sum(1 for result in results if result['success'])
        print(f"成功数量: {success_count}")
        failed_count = len(results) - success_count
        print(f"失败数量: {failed_count}")
        
        for i, result in enumerate(results):
            status = "成功" if result['success'] else "失败"
            print(f"{i+1}. 群组 {result['chat_id']}: {status}")
            if not result['success']:
                print(f"   错误原因: {result['error']}")
        
        print("\n推送测试完成!")
    except Exception as e:
        print(f"\n推送测试失败: {str(e)}")
        raise

if __name__ == "__main__":
    test_create_and_send_weekly_report()
