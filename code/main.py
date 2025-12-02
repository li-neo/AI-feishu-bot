#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
飞书AI周报推送与智能问答机器人主程序
"""

import os
import sys
import lark_oapi as lark
from lark_oapi.api.im.v1 import *

# 导入自定义模块
from config import APP_ID, APP_SECRET
from event_handler import do_p2_im_message_receive_v1

# 事件处理器
event_handler = lark.EventDispatcherHandler.builder(APP_ID, APP_SECRET) \
    .register_p2_im_message_receive_v1(do_p2_im_message_receive_v1) \
    .build()


def start_event_subscription():
    """启动事件订阅"""
    print("Starting event subscription...")
    cli = lark.ws.Client(APP_ID, APP_SECRET,
                        event_handler=event_handler, log_level=lark.LogLevel.DEBUG)
    cli.start()


def main():
    """主函数"""
    print("飞书AI周报推送与智能问答机器人启动")
    
    # 启动事件订阅（用于接收@消息）
    start_event_subscription()
    
    # 注意：实际使用时，发送周报功能应该由定时任务触发
    # 这里仅作为示例，不会自动执行


if __name__ == "__main__":
    main()