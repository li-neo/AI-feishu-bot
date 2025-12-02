#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
为所有添加机器人的群组发送周报
"""

from weekly_report import send_weekly_report_to_groups

def seed_all_weekly_report():
    """为所有添加机器人的群组发送周报"""
    # 1. 直接调用send_weekly_report_to_groups函数，不指定target_chat_ids参数
    # 当target_chat_ids为None时，函数会自动获取所有机器人所在的群组
    print("=== 开始向所有机器人所在群组发送周报 ===")
    
    try:
        results = send_weekly_report_to_groups(
            report_content=None,  # 兼容旧接口，实际不再使用
            target_chat_ids=None,  # 发送给所有机器人所在的群组
            use_card=True  # 使用飞书卡片格式发送
        )
        
        # 2. 打印发送结果
        print(f"\n=== 周报发送结果 ===")
        print(f"总发送数量: {len(results)}")
        success_count = sum(1 for result in results if result['success'])
        print(f"成功数量: {success_count}")
        failed_count = len(results) - success_count
        print(f"失败数量: {failed_count}")
        
        # 3. 详细打印每个群组的发送结果
        print(f"\n=== 详细发送结果 ===")
        for i, result in enumerate(results):
            status = "成功" if result['success'] else "失败"
            print(f"{i+1}. 群组 {result['chat_id']}: {status}")
            if not result['success']:
                print(f"   错误原因: {result['error']}")
        
        print("\n=== 周报发送任务完成 ===")
        return results
    except Exception as e:
        print(f"\nERROR: 周报发送失败: {str(e)}")
        raise

if __name__ == "__main__":
    seed_all_weekly_report()
