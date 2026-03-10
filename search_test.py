#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""百度AI搜索测试脚本"""

import requests
import json
import os
from datetime import datetime

# 读取Token
token = os.getenv("BAIDU_AISEARCH_TOKEN")
if not token:
    raise ValueError("请设置环境变量 BAIDU_AISEARCH_TOKEN 或在 .env.local 文件中配置")

# API配置
url = "https://qianfan.baidubce.com/v2/ai_search/mcp"
headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {token}"
}

# 构建请求
payload = {
    "jsonrpc": "2.0",
    "method": "tools/call",
    "params": {
        "name": "chatCompletions",
        "arguments": {
            "query": "国家电网 电费抄核 自动化抄表 优秀案例"
        }
    },
    "id": f"call-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
}

print("正在调用百度AI搜索...")
print(f"查询: {payload['params']['arguments']['query']}")
print("-" * 50)

# 发送请求
response = requests.post(url, headers=headers, json=payload, timeout=30)

# 处理响应
if response.status_code == 200:
    result = response.json()
    print("搜索成功！")
    print(f"响应ID: {result.get('id')}")
    print("-" * 50)
    
    # 提取内容
    if 'result' in result and 'content' in result['result']:
        content = result['result']['content']
        if isinstance(content, list) and len(content) > 0:
            text = content[0].get('text', '')
            # 保存到文件
            output_file = "D:/opencode/github/sgcc-quality-service-research/search-logs/search-result-20260310.json"
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(result, f, ensure_ascii=False, indent=2)
            print(f"结果已保存到: {output_file}")
            print(f"内容长度: {len(text)} 字符")
        else:
            print("未找到有效内容")
    else:
        print("响应格式异常")
        # 保存完整响应
        output_file = "D:/opencode/github/sgcc-quality-service-research/search-logs/search-result-20260310.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
else:
    print(f"请求失败: HTTP {response.status_code}")
    # 保存错误响应
    output_file = "D:/opencode/github/sgcc-quality-service-research/search-logs/search-result-20260310.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(response.text)
