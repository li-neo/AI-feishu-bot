#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试LLM返回值解析
"""

# 模拟API响应结构
class MockResponseContent:
    def __init__(self, content_type, text=None, url=None):
        self.type = content_type
        self.text = text
        self.url = url

class MockOutput:
    def __init__(self, content_list):
        self.content = content_list

class MockResponse:
    def __init__(self, output_content_list, response_id):
        # 模拟output[0]结构，包含content列表
        self.output = [MockOutput(output_content_list)]
        self.id = response_id

# 测试不同类型的返回值解析

def test_text_only():
    """测试只返回文本的情况"""
    # 模拟API响应
    mock_content = [
        MockResponseContent('output_text', text='你好呀，今天有啥新鲜事儿？'),
        MockResponseContent('output_text', text='这是第二部分内容')
    ]
    mock_response = MockResponse(mock_content, 'test_id_123')
    
    # 测试解析逻辑
    ai_content = ""
    response_message = mock_response.output[0]
    
    for content_item in response_message.content:
        if hasattr(content_item, 'type') and content_item.type == 'output_text':
            if hasattr(content_item, 'text'):
                ai_content += content_item.text
    
    print(f"文本解析结果: {ai_content}")
    assert ai_content == '你好呀，今天有啥新鲜事儿？这是第二部分内容'
    print("✓ 文本解析测试通过")

def test_text_with_image():
    """测试同时返回文本和图片的情况"""
    # 模拟API响应
    mock_content = [
        MockResponseContent('output_text', text='这是一段文本内容，附带一张图片：'),
        MockResponseContent('output_image', url='https://example.com/image.jpg')
    ]
    mock_response = MockResponse(mock_content, 'test_id_456')
    
    # 测试解析逻辑
    ai_content = ""
    response_message = mock_response.output[0]
    
    for content_item in response_message.content:
        if hasattr(content_item, 'type') and content_item.type == 'output_text':
            if hasattr(content_item, 'text'):
                ai_content += content_item.text
        elif hasattr(content_item, 'type') and content_item.type == 'output_image':
            if hasattr(content_item, 'url'):
                ai_content += f"\n[图片: {content_item.url}]"
    
    print(f"文本+图片解析结果: {ai_content}")
    assert ai_content == '这是一段文本内容，附带一张图片：\n[图片: https://example.com/image.jpg]'
    print("✓ 文本+图片解析测试通过")

if __name__ == "__main__":
    print("开始测试LLM返回值解析...")
    test_text_only()
    test_text_with_image()
    print("\n所有测试通过！")
