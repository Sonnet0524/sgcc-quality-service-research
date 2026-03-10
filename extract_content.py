#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""提取搜索结果内容"""

import json

# 读取JSON文件
with open('D:/opencode/github/sgcc-quality-service-research/search-logs/search-result-20260310.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# 提取文本内容
text = data['result']['content'][0]['text']

# 保存到文件
with open('D:/opencode/github/sgcc-quality-service-research/search-logs/search-content-20260310.txt', 'w', encoding='utf-8') as f:
    f.write(text)

print(f"内容已保存，共 {len(text)} 字符")
