#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试多模态消息处理
"""

import json
import sys

# 添加代码目录到路径
sys.path.append('/Users/bytedance/AI/csm_ai/code')

# 模拟飞书事件数据
def test_message_content_parsing():
    """测试消息内容解析逻辑"""
    # 模拟飞书消息数据，包含@机器人和图片
    mock_message_content = {
        "title": "",
        "content": [
            [
                {
                    "tag": "at",
                    "user_id": "@_user_1",
                    "user_name": "CSM-AI",
                    "style": []
                },
                {
                    "tag": "text",
                    "text": "  帮我分析一下图片是什么",
                    "style": []
                }
            ],
            [
                {
                    "tag": "img",
                    "image_key": "img_v3_02sj_bfddac5d-275b-4e06-9050-69d5faaaab8g",
                    "width": 204,
                    "height": 162
                }
            ]
        ]
    }
    
    print("\n测试消息内容解析...")
    print("原始消息内容:", json.dumps(mock_message_content, indent=2))
    
    # 测试解析逻辑
    text_content = ""
    image_keys = []
    
    # 处理结构化消息内容，支持文本和图片
    if isinstance(mock_message_content, dict) and "content" in mock_message_content:
        # 遍历content中的每一行
        for line in mock_message_content["content"]:
            # 遍历行中的每个元素
            for item in line:
                # 处理文本标签
                if item.get("tag") == "text":
                    text_content += item.get("text", "")
                # 处理图片标签
                elif item.get("tag") == "img":
                    image_key = item.get("image_key")
                    if image_key:
                        image_keys.append(image_key)
    
    print(f"解析出的文本: '{text_content}'")
    print(f"解析出的图片key: {image_keys}")
    
    # 验证解析结果
    assert text_content.strip() == "帮我分析一下图片是什么"
    assert len(image_keys) == 1
    assert image_keys[0] == "img_v3_02sj_bfddac5d-275b-4e06-9050-69d5faaaab8g"
    
    print("✓ 消息内容解析测试通过")
    return True

def test_llm_input_construction():
    """测试LLM输入构建逻辑"""
    from llm import llm_request
    
    print("\n测试LLM输入构建...")
    
    # 测试纯文本输入
    text_input = "帮我分析一下这个问题"
    print(f"纯文本输入: '{text_input}'")
    
    # 测试包含图片URL的输入
    multimodal_input = "帮我分析一下图片是什么\n图片URL: https://black-neo.tos-cn-beijing.volces.com/screenshot-20251118-153229.png，\n https://black-neo.tos-cn-beijing.volces.com/screenshot-20251118-153229.png"
    print(f"多模态输入: '{multimodal_input}'")
    
    # 测试解析逻辑
    has_images = "图片URL:" in multimodal_input
    assert has_images == True
    
    # 分离文本和图片URL
    text_part = ""
    image_urls = []
    is_image_url_section = False
    urls_part = ""
    
    # 分割输入，提取图片URL
    lines = multimodal_input.split("\n")
    for line in lines:
        line = line.strip()
        if line.startswith("图片URL:"):
            is_image_url_section = True
            # 提取当前行的图片URL部分
            urls_part += line.replace("图片URL:", "").strip() + " "
        elif is_image_url_section:
            # 如果是图片URL部分的后续行，直接添加
            urls_part += line + " "
        else:
            # 普通文本行
            if line:
                text_part += line + "\n"
    
    text_part = text_part.strip()
    
    # 处理URL部分，支持中英文逗号分隔
    if urls_part:
        # 替换中文逗号为英文逗号
        urls_part = urls_part.replace("，", ",")
        # 分割URL列表并清理
        raw_urls = urls_part.split(",")
        for url in raw_urls:
            # 清理URL中的多余空格和反引号
            clean_url = url.strip().strip("`")
            if clean_url:
                image_urls.append(clean_url)
    
    print(f"分离后的文本: '{text_part}'")
    print(f"提取的图片URL: {image_urls}")
    
    # 更新断言，使用正确的预期结果
    expected_text = "帮我分析一下图片是什么"
    expected_urls = [
        "https://black-neo.tos-cn-beijing.volces.com/screenshot-20251118-153229.png",
        "https://black-neo.tos-cn-beijing.volces.com/screenshot-20251118-153229.png"
    ]
    
    assert text_part == expected_text, f"预期文本: '{expected_text}', 实际文本: '{text_part}'"
    assert len(image_urls) == len(expected_urls), f"预期图片URL数量: {len(expected_urls)}, 实际数量: {len(image_urls)}"
    assert image_urls == expected_urls, f"预期图片URL: {expected_urls}, 实际URL: {image_urls}"
    
    # 构建多模态输入内容（与官方示例格式一致）
    user_content = []
    
    # 添加文本内容
    if text_part:
        user_content.append({
            "type": "input_text",
            "text": text_part
        })
    
    # 添加图片内容
    for url in image_urls:
        user_content.append({
            "type": "input_image",
            "image_url": url
        })
    
    print(f"构建的多模态内容: {json.dumps(user_content, indent=2)}")
    
    assert len(user_content) == 3  # 1个文本 + 2个图片
    assert user_content[0]["type"] == "input_text"
    assert user_content[1]["type"] == "input_image"
    assert user_content[2]["type"] == "input_image"
    
    print("✓ LLM输入构建测试通过")
    return True

if __name__ == "__main__":
    print("开始测试多模态消息处理...")
    test_message_content_parsing()
    test_llm_input_construction()
    print("\n所有测试通过！")
