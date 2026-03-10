# 百度AI搜索能力使用指南

## 概述

本目录包含百度AI搜索的完整实现，包括：
- `baidu-search.md` - 百度AI搜索技能文档
- `baidu_search_api.py` - Python实现脚本
- `README.md` - 使用指南

## 两种使用方式

### 方式1：MCP工具（推荐）

**前提条件**：
- MCP工具已正确配置
- 会话中MCP工具可用

**使用方法**：
```json
{
  "name": "AIsearch",
  "arguments": {
    "query": "国家电网 业扩报装 优秀案例",
    "model": "ERNIE-3.5-8K",
    "temperature": 0.3,
    "instruction": "提取典型案例的关键信息：单位名称、服务对象、服务模式、创新点、服务效果"
  }
}
```

### 方式2：Python脚本（备选）

**前提条件**：
- Python 3.7+
- requests库已安装
- BAIDU_AISEARCH_TOKEN已配置

**安装依赖**：
```bash
pip install requests
```

**配置Token**：

方法1：环境变量
```bash
export BAIDU_AISEARCH_TOKEN="bce-v3/ALTAK-..."
```

方法2：配置文件
创建 `D:/opencode/github/.env.local` 文件：
```
BAIDU_AISEARCH_TOKEN=bce-v3/ALTAK-...
```

**使用方法**：

基础搜索：
```bash
python skills/baidu_search_api.py --query "国家电网 业扩报装 优秀案例"
```

AI搜索（带总结）：
```bash
python skills/baidu_search_api.py \
  --query "国家电网 业扩报装 优秀案例" \
  --model "ERNIE-3.5-8K" \
  --temperature 0.3 \
  --instruction "总结为3个要点"
```

保存结果到文件：
```bash
python skills/baidu_search_api.py \
  --query "国家电网 业扩报装 优秀案例" \
  --output results.json
```

## 搜索日志记录

### 自动记录

每次调用百度AI搜索API，都会自动记录：

1. **调用前日志**：记录查询参数、当前用量
2. **调用后日志**：记录结果、响应时间、用量更新
3. **用量统计**：维护每日用量和剩余额度

### 日志位置

- **每日日志**：`search-logs/YYYY-MM-DD.jsonl`
- **用量统计**：`search-logs/usage-stats.json`

### 日志格式

调用前日志：
```json
{
  "timestamp": "2026-03-10T10:30:00.000Z",
  "call_id": "call-20260310-001",
  "phase": "before",
  "input": {
    "query": "搜索关键词",
    "parameters": {
      "model": "ERNIE-3.5-8K",
      "temperature": 0.3
    }
  },
  "usage_before": {
    "daily_total": 10,
    "daily_limit": 1000,
    "remaining": 990
  }
}
```

调用后日志（成功）：
```json
{
  "timestamp": "2026-03-10T10:30:01.234Z",
  "call_id": "call-20260310-001",
  "phase": "after",
  "output": {
    "status": "success",
    "result_count": 5,
    "response_time_ms": 1234,
    "request_id": "xxx-xxx-xxx"
  },
  "results_preview": [
    {"id": 1, "title": "结果标题1", "url": "https://..."}
  ],
  "usage_after": {
    "remaining": 989
  }
}
```

调用后日志（失败）：
```json
{
  "timestamp": "2026-03-10T10:30:01.234Z",
  "call_id": "call-20260310-001",
  "phase": "after",
  "output": {
    "status": "failed",
    "error_code": 401,
    "error_message": "认证失败",
    "response_time_ms": 234
  },
  "retry_suggestion": "检查API Token是否正确",
  "usage_after": {
    "remaining": 989
  }
}
```

## 最佳实践

### 1. 参数选择

| 场景 | 推荐配置 |
|------|---------|
| 快速获取原始信息 | 仅使用query参数 |
| 需要内容总结 | model + instruction |
| 事实性查询 | model + temperature: 0.1-0.3 |
| 创意性内容 | model + temperature: 0.5-0.7 |

### 2. 查询构建

- ✅ 使用简洁明确的关键词组合
- ✅ 复杂查询拆分为多个简单查询
- ❌ 避免过于宽泛或模糊的词语

### 3. 用量监控

每日检查用量统计：
```bash
cat search-logs/usage-stats.json
```

## 成本控制

- **免费额度**：1000次/天
- **超出后计费**：0.036元/次
- **监控建议**：剩余额度 < 200时，谨慎使用

## 故障排除

### 问题1：Token未找到

**错误信息**：
```
ValueError: 未找到BAIDU_AISEARCH_TOKEN
```

**解决方法**：
1. 检查环境变量是否设置
2. 检查.env.local文件是否存在
3. 确认Token格式正确

### 问题2：认证失败

**错误信息**：
```
HTTP 401: 认证失败
```

**解决方法**：
1. 检查Token是否过期
2. 检查Token格式是否正确（应以"bce-v3/"开头）
3. 重新获取Token

### 问题3：请求频率过高

**错误信息**：
```
HTTP 429: 请求过于频繁
```

**解决方法**：
1. 降低请求频率（限速：3 QPS）
2. 等待几秒后重试
3. 实现请求队列管理

## API文档参考

- [百度千帆控制台](https://console.bce.baidu.com/qianfan/)
- [百度AI搜索文档](https://cloud.baidu.com/doc/qianfan/s/2mh4su4uy)

## 示例脚本

### 批量搜索示例

```python
#!/usr/bin/env python3
import sys
sys.path.insert(0, r'D:\opencode\github\sgcc-quality-service-research')

from skills.baidu_search_api import BaiduAISearch

# 创建搜索客户端
client = BaiduAISearch()

# 定义搜索任务
queries = [
    "国家电网 业扩报装 优秀案例",
    "供电公司 电费回收 服务案例",
    "国网 网格化服务 典型做法"
]

# 批量搜索
for query in queries:
    print(f"\n搜索: {query}")
    result = client.search(
        query=query,
        model="ERNIE-3.5-8K",
        temperature=0.3,
        instruction="总结为3个要点"
    )
    print(f"结果数量: {result.get('result_count', 0)}")
    print(f"剩余额度: {result.get('usage', {}).get('remaining', 0)}")
```

### 带日志分析的搜索

```python
#!/usr/bin/env python3
import json
from pathlib import Path
from skills.baidu_search_api import BaiduAISearch

def analyze_search_logs():
    """分析搜索日志"""
    log_dir = Path("search-logs")
    stats_file = log_dir / "usage-stats.json"
    
    if stats_file.exists():
        with open(stats_file, 'r', encoding='utf-8') as f:
            stats = json.load(f)
        
        print("用量统计：")
        for date, usage in stats.get("daily_usage", {}).items():
            print(f"{date}: {usage['total_calls']} 次, 剩余 {usage['remaining']} 次")
        
        print("\n月度汇总：")
        for month, summary in stats.get("monthly_summary", {}).items():
            print(f"{month}: {summary['total_calls']} 次")

if __name__ == "__main__":
    analyze_search_logs()
```

## 维护者

- **创建时间**：2026-03-10
- **最后更新**：2026-03-10
- **维护者**：Research Agent
