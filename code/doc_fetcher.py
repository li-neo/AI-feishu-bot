#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
飞书文档数据获取模块
用于从飞书文档获取周报数据并转换为卡片所需格式
"""

import json
import requests
import sys
import datetime
from typing import Dict, Any, List, Optional
from auth import get_tenant_access_token
from config import WEEKLY_REPORT_FILTER_DAYS, DEFAULT_WEEKLY_REPORT_TITLE


def fetch_doc_content(tenant_access_token: str, doc_token: str) -> Dict[str, Any]:
    """
    从飞书文档获取内容
    
    Args:
        tenant_access_token: 租户访问令牌
        doc_token: 飞书文档token
        
    Returns:
        Dict[str, Any]: 文档内容
    """
    url = f"https://open.feishu.cn/open-apis/docx/v1/documents/{doc_token}/raw_content"
    headers = {
        "Authorization": f"Bearer {tenant_access_token}",
        "Content-Type": "application/json; charset=utf-8"
    }
    
    try:
        print(f"GET: {url}")
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        result = response.json()
        print(f"Response: {json.dumps(result)}")
        
        if result.get("code", 0) != 0:
            error_msg = f"failed to fetch doc content: {result.get('msg', 'unknown error')}"
            print(f"ERROR: {error_msg}", file=sys.stderr)
            raise Exception(error_msg)
            
        return result
        
    except Exception as e:
        error_msg = f"Error fetching doc content: {e}"
        if hasattr(e, 'response') and e.response is not None:
            error_msg += f" Response: {e.response.text}"
        print(f"ERROR: {error_msg}", file=sys.stderr)
        raise


def fetch_sheet_content(tenant_access_token: str, spreadsheet_token: str, sheet_id: str) -> Dict[str, Any]:
    """
    从飞书表格获取内容
    
    Args:
        tenant_access_token: 租户访问令牌
        spreadsheet_token: 飞书表格token
        sheet_id: 表格sheet ID
        
    Returns:
        Dict[str, Any]: 表格内容
    """
    url = f"https://open.feishu.cn/open-apis/sheets/v2/spreadsheets/{spreadsheet_token}/values/{sheet_id}"
    headers = {
        "Authorization": f"Bearer {tenant_access_token}",
        "Content-Type": "application/json; charset=utf-8"
    }
    
    try:
        print(f"GET: {url}")
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        result = response.json()
        print(f"Response: {json.dumps(result)}")
        
        if result.get("code", 0) != 0:
            error_msg = f"failed to fetch sheet content: {result.get('msg', 'unknown error')}"
            print(f"ERROR: {error_msg}", file=sys.stderr)
            raise Exception(error_msg)
            
        return result
        
    except Exception as e:
        error_msg = f"Error fetching sheet content: {e}"
        if hasattr(e, 'response') and e.response is not None:
            error_msg += f" Response: {e.response.text}"
        print(f"ERROR: {error_msg}", file=sys.stderr)
        raise


def fetch_bitable_content(tenant_access_token: str, bitable_token: str, table_id: str) -> Dict[str, Any]:
    """
    从飞书多维表格获取内容
    
    Args:
        tenant_access_token: 租户访问令牌
        bitable_token: 飞书多维表格token
        table_id: 多维表格中的表ID
        
    Returns:
        Dict[str, Any]: 多维表格内容
    """
    # 飞书多维表格API端点
    url = f"https://open.feishu.cn/open-apis/bitable/v1/apps/{bitable_token}/tables/{table_id}/records"
    headers = {
        "Authorization": f"Bearer {tenant_access_token}",
        "Content-Type": "application/json; charset=utf-8"
    }
    
    try:
        print(f"GET: {url}")
        response = requests.get(url, headers=headers)
        
        # 增强错误处理，提供更清晰的错误信息
        if response.status_code == 400:
            error_response = response.json()
            if error_response.get("code") == 99991672:
                # 权限错误处理
                error_msg = f"Failed to fetch bitable content: Permission denied. Error code: {error_response.get('code')}"
                error_msg += f"\nPlease enable the required permissions for your Feishu app at:"
                error_msg += f"\nhttps://open.feishu.cn/app/cli_a9afe48337fb5bde/auth?q=bitable:app:readonly,bitable:app,base:record:retrieve"
                error_msg += f"\nError details: {error_response.get('msg')}"
                print(f"ERROR: {error_msg}", file=sys.stderr)
                raise Exception(error_msg)
        
        response.raise_for_status()
        
        result = response.json()
        print(f"Response: {json.dumps(result)}")
        
        if result.get("code", 0) != 0:
            error_msg = f"failed to fetch bitable content: {result.get('msg', 'unknown error')}"
            print(f"ERROR: {error_msg}", file=sys.stderr)
            raise Exception(error_msg)
            
        return result
        
    except Exception as e:
        error_msg = f"Error fetching bitable content: {e}"
        if hasattr(e, 'response') and e.response is not None:
            error_msg += f" Response: {e.response.text}"
        print(f"ERROR: {error_msg}", file=sys.stderr)
        raise


def update_bitable_record(tenant_access_token: str, bitable_token: str, table_id: str, record_id: str, field_name: str, image_key: str) -> bool:
    """
    更新飞书多维表格记录，将image_key写入到指定字段
    
    Args:
        tenant_access_token: 租户访问令牌
        bitable_token: 飞书多维表格token
        table_id: 多维表格中的表ID
        record_id: 记录ID
        field_name: 要更新的字段名称
        image_key: 要写入的image_key
        
    Returns:
        bool: 更新是否成功
    """
    # 飞书多维表格API端点，用于更新记录
    url = f"https://open.feishu.cn/open-apis/bitable/v1/apps/{bitable_token}/tables/{table_id}/records/{record_id}"
    headers = {
        "Authorization": f"Bearer {tenant_access_token}",
        "Content-Type": "application/json; charset=utf-8"
    }
    
    # 构建请求体，只更新指定字段
    payload = {
        "fields": {
            field_name: image_key
        }
    }
    
    try:
        print(f"PUT: {url}")
        print(f"Payload: {json.dumps(payload)}")
        response = requests.put(url, headers=headers, json=payload)
        
        # 增强错误处理，提供更清晰的错误信息
        if response.status_code == 400:
            error_response = response.json()
            if error_response.get("code") == 99991672:
                # 权限错误处理
                error_msg = f"Failed to update bitable record: Permission denied. Error code: {error_response.get('code')}"
                error_msg += f"\nPlease enable the required permissions for your Feishu app at:"
                error_msg += f"\nhttps://open.feishu.cn/app/cli_a9afe48337fb5bde/auth?q=bitable:app:readonly,bitable:app,base:record:write,base:record:retrieve"
                error_msg += f"\nError details: {error_response.get('msg')}"
                print(f"ERROR: {error_msg}", file=sys.stderr)
                return False
        
        response.raise_for_status()
        
        result = response.json()
        print(f"Response: {json.dumps(result)}")
        
        if result.get("code", 0) != 0:
            error_msg = f"failed to update bitable record: {result.get('msg', 'unknown error')}"
            print(f"ERROR: {error_msg}", file=sys.stderr)
            return False
            
        return True
        
    except Exception as e:
        error_msg = f"Error updating bitable record: {e}"
        if hasattr(e, 'response') and e.response is not None:
            error_msg += f" Response: {e.response.text}"
        print(f"ERROR: {error_msg}", file=sys.stderr)
        return False


def get_image_key(tenant_access_token: str, file_token: str) -> str:
    """
    根据file_token获取飞书图片image_key
    
    Args:
        tenant_access_token: 租户访问令牌
        file_token: 文件token
        
    Returns:
        str: 图片image_key
    """
    # Step 1: 下载图片内容
    download_url = f"https://open.feishu.cn/open-apis/drive/v1/medias/{file_token}/download"
    headers = {
        "Authorization": f"Bearer {tenant_access_token}",
    }
    
    try:
        print(f"GET: {download_url}")
        response = requests.get(download_url, headers=headers)
        response.raise_for_status()
        image_content = response.content
    except Exception as e:
        error_msg = f"Error downloading image: {e}"
        if hasattr(e, 'response') and e.response is not None:
            error_msg += f" Response: {e.response.text}"
        print(f"ERROR: {error_msg}", file=sys.stderr)
        raise
    
    # Step 2: 上传图片获取image_key
    upload_url = "https://open.feishu.cn/open-apis/im/v1/images"
    upload_headers = {
        "Authorization": f"Bearer {tenant_access_token}",
    }
    
    # 构建请求体
    files = {
        "image": (f"image_{file_token}.png", image_content, "image/png"),
    }
    
    data = {
        "image_type": "message",
    }
    
    try:
        print(f"POST: {upload_url}")
        response = requests.post(upload_url, headers=upload_headers, files=files, data=data)
        response.raise_for_status()
        
        result = response.json()
        print(f"Response: {json.dumps(result)}")
        
        if result.get("code", 0) != 0:
            error_msg = f"failed to upload image: {result.get('msg', 'unknown error')}"
            print(f"ERROR: {error_msg}", file=sys.stderr)
            raise Exception(error_msg)

            
        return result["data"]["image_key"]
        
    except Exception as e:
        error_msg = f"Error uploading image: {e}"
        if hasattr(e, 'response') and e.response is not None:
            error_msg += f" Response: {e.response.text}"
        print(f"ERROR: {error_msg}", file=sys.stderr)
        raise


def extract_img_keys(img_field: Any, tenant_access_token: str, bitable_token: Optional[str] = None, table_id: Optional[str] = None, record_id: Optional[str] = None, field_name: Optional[str] = None) -> List[str]:
    """
    从图片字段中提取图片key列表
    
    Args:
        img_field: 图片字段数据，可能是列表（附件类型）或字符串（文本类型）
        tenant_access_token: 租户访问令牌，用于获取图片image_key
        bitable_token: 飞书多维表格token，用于更新记录（可选）
        table_id: 多维表格中的表ID，用于更新记录（可选）
        record_id: 记录ID，用于更新记录（可选）
        field_name: 图片字段名称，用于更新记录（可选）
        
    Returns:
        List[str]: 提取的图片key列表
    """
    img_keys = []
    print(f"DEBUG: Processing img_field: {img_field}, type: {type(img_field)}")
    if isinstance(img_field, list):
        # 附件类型字段，返回格式为[{"file_token": "KUJvbTl9...", "name": "xxx.jpg", "type": "image"}, ...]
        print(f"DEBUG: img_field is list, length: {len(img_field)}")
        for i, img_item in enumerate(img_field):
            print(f"DEBUG: img_item {i}: {img_item}, type: {type(img_item)}")
            if isinstance(img_item, dict):
                # 检查是否有file_token字段
                if "file_token" in img_item:
                    file_token = img_item["file_token"]
                    print(f"DEBUG: Found file_token: {file_token}")
                    if file_token.startswith("img_"):
                        # 如果已经是img_key格式，直接使用
                        img_keys.append(file_token)
                    else:
                        # 否则调用API获取image_key
                        try:
                            image_key = get_image_key(tenant_access_token, file_token)

                            # 写入image_key 到多维表格的image_key 字段中
                            if bitable_token and table_id and record_id and field_name:
                                update_bitable_record(tenant_access_token, bitable_token, table_id, record_id, field_name, image_key)
                            img_keys.append(image_key)
                        except Exception as e:
                            print(f"WARN: Failed to get image_key for file_token {file_token}: {e}")
                            continue
            else:
                print(f"DEBUG: img_item {i} is not a dict, skipping")
    elif isinstance(img_field, str) and img_field:
        # 文本类型字段
        print(f"DEBUG: img_field is string: {img_field}")
        if img_field.startswith("img_"):
            # 如果已经是img_key格式，直接使用
            img_keys.append(img_field)
        else:
            # 否则尝试作为file_token处理
            try:
                image_key = get_image_key(tenant_access_token, img_field)
                # 将image_key 重新写入到多维表格中，写入到image_key字段
                if bitable_token and table_id and record_id and field_name:
                    update_bitable_record(tenant_access_token, bitable_token, table_id, record_id, field_name, image_key)
                img_keys.append(image_key)
            except Exception as e:
                print(f"WARN: Failed to get image_key for string {img_field}: {e}")
    else:
        print(f"DEBUG: img_field is not a valid type, skipping")
    print(f"DEBUG: Extracted img_keys: {img_keys}")
    return img_keys


def build_pictures_list(img_fields: List[Any], tenant_access_token: str, bitable_token: Optional[str] = None, table_id: Optional[str] = None, record_id: Optional[str] = None, field_names: Optional[List[str]] = None) -> List[Dict[str, Any]]:
    """
    构建周报所需的pictures列表
    
    Args:
        img_fields: 图片字段列表
        tenant_access_token: 租户访问令牌，用于获取图片image_key
        bitable_token: 飞书多维表格token，用于更新记录（可选）
        table_id: 多维表格中的表ID，用于更新记录（可选）
        record_id: 记录ID，用于更新记录（可选）
        field_names: 图片字段名称列表，用于更新记录（可选）
        
    Returns:
        List[Dict[str, Any]]: 构建的pictures列表，每个元素包含img_key和i18n_img_key
    """
    pictures = []
    for i, img_field in enumerate(img_fields):
        # 提取图片key
        field_name = field_names[i] if field_names and i < len(field_names) else None
        img_keys = extract_img_keys(img_field, tenant_access_token, bitable_token, table_id, record_id, field_name)
        # 添加到pictures列表
        for img_key in img_keys:
            pictures.append({
                "img_key": img_key,
                "i18n_img_key": {"zh_cn": img_key}
            })
    return pictures


def parse_sheet_data(sheet_data: Dict[str, Any], tenant_access_token: str, bitable_token: Optional[str] = None, table_id: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    解析飞书表格数据并转换为周报item格式
    
    Args:
        sheet_data: 从飞书表格或多维表格获取的原始数据
        tenant_access_token: 租户访问令牌，用于获取图片image_key
        bitable_token: 飞书多维表格token，用于更新记录（可选）
        table_id: 多维表格中的表ID，用于更新记录（可选）
        
    Returns:
        List[Dict[str, Any]]: 转换后的周报items列表
    """
    items = []
    
    # 处理普通飞书表格数据
    if "data" in sheet_data and "valueRange" in sheet_data["data"]:
        rows = sheet_data["data"]["valueRange"]["values"]
        if len(rows) > 1:
            # 跳过标题行，从第二行开始处理数据
            for row in rows[1:]:
                if len(row) < 5:  # 确保有足够的列数据
                    continue
                    
                # 解析每行数据
                name = row[0] if row[0] else ""
                desc = row[1] if row[1] else ""
                img_key1 = row[2] if len(row) > 2 and row[2] else ""
                img_key2 = row[3] if len(row) > 3 and row[3] else ""
                url = row[4] if len(row) > 4 and row[4] else ""
                
                # 构建pictures列表
                pictures = build_pictures_list([img_key1, img_key2], tenant_access_token)
                
                # 处理换行符，先解码JSON转义序列\n为实际的\n，再转换为<br>标签
                if desc:
                    # 替换JSON转义的换行符\n为实际换行符
                    desc = desc.replace('\\n', '\n')
                    # 再将实际换行符转换为HTML <br>标签
                    desc = desc.replace('\n', '<br>')
                
                # 构建item
                item = {
                    "name": name,
                    "desc": desc,
                    "pictures": pictures,
                    "url": {
                        "pc_url": "",
                        "android_url": "",
                        "ios_url": "",
                        "url": url
                    }
                }
                
                items.append(item)
    
    # 处理飞书多维表格数据
    elif "data" in sheet_data and "items" in sheet_data["data"]:
        records = sheet_data["data"]['items']
        
        for record in records:
            # 多维表格数据存储在fields字段中
            fields = record.get("fields", {})
            
            # 获取记录ID，用于后续更新记录
            record_id = record.get("record_id", "")
            print(f"DEBUG: record_id: {record_id}")
            
            # 解析字段数据，支持不同的列名映射
            name = fields.get("名称", fields.get("name", ""))
            desc = fields.get("描述", fields.get("desc", ""))
            
            # 支持更多可能的URL字段名称
            url_field = fields.get("URL", fields.get("url", fields.get("链接", fields.get("link", ""))))
            time_str = fields.get("Time", fields.get("time", ""))
            
            # 解析URL字段，支持超链接类型（对象）和文本类型
            url = ""
            url_text = ""
            if isinstance(url_field, dict):
                # 超链接类型，包含text和url属性
                url = url_field.get("url", "")
                url_text = url_field.get("text", "")
            else:
                # 文本类型，如果内容是"AI-周报"，则设置为空，因为它不是一个有效的URL
                url_field_str = str(url_field) if url_field else ""
                if url_field_str == "AI-周报":
                    url = ""
                    url_text = ""
                else:
                    # 否则直接使用
                    url = url_field_str
                    url_text = url_field_str
            
            # 过滤掉空记录（至少需要有名称字段）
            if not name:
                continue
            
            # 过滤：确保Time字段存在且在配置的天数内，先校验时间可以减少后续不必要的计算
            record_time = None
            if time_str:
                try:
                    # 解析时间，支持多种格式
                    if isinstance(time_str, str):
                        # 尝试不同的时间格式解析
                        time_formats = ["%Y-%m-%d", "%Y-%m-%d %H:%M:%S", "%Y/%m/%d", "%Y/%m/%d %H:%M:%S"]
                        for fmt in time_formats:
                            try:
                                record_time = datetime.datetime.strptime(time_str.split('T')[0], fmt) if 'T' in time_str else datetime.datetime.strptime(time_str, fmt)
                                break
                            except ValueError:
                                continue
                    elif isinstance(time_str, (int, float)):
                        # 处理数字类型的时间戳（毫秒或秒）
                        timestamp = float(time_str)
                        # 判断是毫秒还是秒为单位
                        if timestamp > 1e12:  # 大于1e12通常是毫秒
                            record_time = datetime.datetime.fromtimestamp(timestamp / 1000)
                        else:  # 否则是秒
                            record_time = datetime.datetime.fromtimestamp(timestamp)
                    
                    if record_time:
                        # 计算过滤日期
                        filter_date = datetime.datetime.now() - datetime.timedelta(days=WEEKLY_REPORT_FILTER_DAYS)
                        # 如果记录时间早于过滤日期，则跳过，减少后续不必要的计算
                        if record_time < filter_date:
                            print(f"DEBUG: Skipping record with time {record_time}, which is before filter date {filter_date}")
                            continue
                except Exception as e:
                    # 如果时间解析失败，不影响记录处理，继续保留
                    print(f"DEBUG: Failed to parse time_str {time_str}: {e}")
            
            # 处理图片字段，优先从image_key字段读取值
            # 1. 先检查是否有专门的image_key字段
            img_key1 = fields.get("image_key1", "")
            img_key2 = fields.get("image_key2", "")
            
            # 2. 如果image_key字段为空，再使用附件字段
            img_field1 = ""
            img_field2 = ""
            if not img_key1:
                img_field1 = fields.get("image1", fields.get("图片1", fields.get("image", fields.get("附件", fields.get("attachment1", "")))))
            if not img_key2:
                img_field2 = fields.get("image2", fields.get("图片2", fields.get("附件2", fields.get("attachment2", ""))))
            
            # 构建pictures列表
            # 使用专门的image_key字段来存储生成的image_key，而不是尝试更新附件类型字段
            pictures = build_pictures_list(
                [img_key1 if img_key1 else img_field1, img_key2 if img_key2 else img_field2], 
                tenant_access_token, 
                bitable_token, 
                table_id, 
                record_id, 
                ["image_key1", "image_key2"]  # 使用专门的image_key字段来存储image_key
            )
            
            # 处理换行符，先解码JSON转义序列\n为实际的\n，再转换为<br>标签
            if desc:
                # 替换JSON转义的换行符\n为实际换行符
                desc = desc.replace('\\n', '\n')
                # 再将实际换行符转换为HTML <br>标签
                desc = desc.replace('\n', '<br>')
            
            # 构建item
            item = {
                "name": name,
                "desc": desc,
                "pictures": pictures,
                "url": {
                    "pc_url": url,
                    "android_url": url,
                    "ios_url": url,
                    "url": url
                }
            }
            
            items.append(item)
    
    return items


def get_weekly_report_data(doc_token: Optional[str] = None, spreadsheet_token: Optional[str] = None, sheet_id: Optional[str] = None, bitable_token: Optional[str] = None, table_id: Optional[str] = None) -> Dict[str, Any]:
    """
    获取周报数据
    
    Args:
        doc_token: 飞书文档token（可选）
        spreadsheet_token: 飞书表格token（可选）
        sheet_id: 表格sheet ID（可选）
        bitable_token: 飞书多维表格token（可选）
        table_id: 多维表格中的表ID（可选）
        
    Returns:
        Dict[str, Any]: 包含common和items的周报数据
    """
    # 获取租户访问令牌
    tenant_access_token, error = get_tenant_access_token()
    if error or not tenant_access_token:
        raise Exception(f"Failed to get tenant access token: {error}")
    
    # 从飞书多维表格获取数据
    if bitable_token and table_id:
        bitable_content = fetch_bitable_content(tenant_access_token, bitable_token, table_id)
        items = parse_sheet_data(bitable_content, tenant_access_token, bitable_token, table_id)
        common = "本周AI动态速览"  # 默认标题，可从表格或文档获取
        
        return {
            "common": common,
            "items": items
        }
    
    # 从普通飞书表格获取数据
    elif spreadsheet_token and sheet_id:
        sheet_content = fetch_sheet_content(tenant_access_token, spreadsheet_token, sheet_id)
        items = parse_sheet_data(sheet_content, tenant_access_token)
        common = "本周AI动态速览"  # 默认标题，可从表格或文档获取
        
        return {
            "common": common,
            "items": items
        }
    
    # 从文档获取数据（需要根据实际文档格式调整解析逻辑）
    elif doc_token:
        doc_content = fetch_doc_content(tenant_access_token, doc_token)
        # 这里需要根据实际文档格式解析common和items
        # 示例：简单返回默认值
        return {
            "common": DEFAULT_WEEKLY_REPORT_TITLE,
            "items": []
        }
    
    else:
        raise Exception("Either doc_token, spreadsheet_token + sheet_id, or bitable_token + table_id must be provided")