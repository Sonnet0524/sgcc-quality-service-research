---
skill: baidu-search
category: tool
depends_on: []
mcp_server: aisearch-mcp-server
tool: chatCompletions
---

# 百度AI搜索能力

> 通过MCP协议调用百度AI搜索，获取实时信息

---

## 📋 能力定义

使用百度AI搜索MCP服务器进行实时信息搜索，支持：
- **基础搜索**：直接返回原始搜索结果
- **AI搜索**：使用大模型对搜索结果进行智能总结

## 🎯 使用场景

- 需要获取最新的实时信息
- 需要搜索新闻、技术文档、教程等
- 需要对搜索结果进行智能总结和分析
- 需要多模态搜索（网页、图片、视频）

## 🔧 MCP配置

### 服务器信息

| 项目 | 内容 |
|------|------|
| **服务器名称** | `aisearch-mcp-server` |
| **工具名称** | `chatCompletions` |
| **URL** | `https://qianfan.baidubce.com/v2/ai_search/mcp` |
| **协议** | JSON-RPC 2.0 |

### 配置文件位置

已在 `opencode.json` 中配置MCP服务器，所有Agent均可使用。

## 🛠️ 工具参数

### chatCompletions 工具

| 参数 | 类型 | 必须 | 说明 |
|------|------|------|------|
| **query** | string | ✅ 是 | 搜索查询关键词或短语 |
| **model** | string | ❌ 否 | 大模型名称（如 `ERNIE-3.5-8K`），不指定则返回原始结果 |
| **instruction** | string | ❌ 否 | 控制搜索结果输出风格和格式 |
| **temperature** | float | ❌ 否 | 模型输出随机性，范围 (0, 1]，默认 1e-10 |
| **top_p** | float | ❌ 否 | 核采样参数，默认 1e-10 |
| **resource_type_filter** | list | ❌ 否 | 资源类型和返回数量 |

## 📝 使用示例

### 基础搜索示例

```json
{
  "query": "北京有哪些旅游景区"
}
```

返回原始搜索结果，不经过LLM处理。

### AI智能总结示例

```json
{
  "query": "人工智能最新发展趋势",
  "model": "ERNIE-3.5-8K",
  "temperature": 0.3,
  "instruction": "总结为3个要点"
}
```

使用大模型对搜索结果进行智能总结。

### 多模态搜索示例

```json
{
  "query": "Python机器学习教程",
  "resource_type_filter": [
    {"type": "web", "top_k": 5},
    {"type": "video", "top_k": 3}
  ]
}
```

同时返回网页和视频类型的搜索结果。

## 💡 最佳实践

### 1. 参数选择指南

| 场景 | 推荐配置 |
|------|---------|
| 快速获取原始信息 | 仅使用 `query` 参数 |
| 需要内容总结 | 添加 `model: "ERNIE-3.5-8K"` |
| 事实性查询 | `model` + `temperature: 0.1-0.3` |
| 创意性内容 | `model` + `temperature: 0.5-0.7` |
| 多类型结果 | 使用 `resource_type_filter` |

### 2. Query构建建议

- ✅ 使用简洁明确的关键词组合
- ✅ 复杂查询拆分为多个简单查询
- ❌ 避免过于宽泛或模糊的词语

### 3. 资源类型配置

```json
// 网页搜索（默认）
{"type": "web", "top_k": 10}

// 视频搜索
{"type": "video", "top_k": 5}

// 图片搜索
{"type": "image", "top_k": 5}

// 多类型组合
[
  {"type": "web", "top_k": 5},
  {"type": "video", "top_k": 3},
  {"type": "image", "top_k": 2}
]
```

## 🔄 工作流程

### ⚠️ Step 0: 记录搜索日志（必须执行）

**每次调用前必须记录搜索日志**，用于跟踪接口质量和用量。

#### 记录内容

```json
{
  "timestamp": "2026-03-09T10:30:00.000Z",
  "call_id": "call-20260309-001",
  "input": {
    "query": "搜索关键词",
    "parameters": {
      "model": "ERNIE-3.5-8K",
      "temperature": 0.3,
      "resource_type_filter": [{"type": "web", "top_k": 5}]
    }
  },
  "output": {
    "status": "success",
    "result_count": 5,
    "response_time_ms": 1234,
    "request_id": "xxx-xxx-xxx"
  },
  "usage": {
    "daily_total": 15,
    "daily_limit": 1000,
    "remaining": 985
  }
}
```

#### 记录位置

- **日志文件**: `search-logs/YYYY-MM-DD.jsonl`
- **用量统计**: `search-logs/usage-stats.json`

#### 维护流程

1. **调用前**：检查今日剩余额度，记录调用意图
2. **调用后**：记录实际结果、响应时间、状态
3. **异常时**：记录错误信息、错误码、重试建议

---

### Step 1: 确定搜索需求

- 需要什么类型的信息？
- 是否需要AI总结？
- 需要多少条结果？

### Step 2: 构建查询参数

根据需求选择合适的参数组合。

### Step 3: 调用MCP工具

通过MCP协议调用 `AIsearch` 工具。

### Step 4: 处理搜索结果

- 分析返回的搜索结果
- 提取关键信息
- 整理和归纳

### Step 5: 更新搜索日志（必须执行）

记录实际返回结果，更新用量统计。

---

## 📊 搜索记录与用量跟踪

### 记录文件结构

```
search-logs/
├── 2026-03-09.jsonl          # 每日搜索记录（JSONL格式）
├── 2026-03-10.jsonl
├── ...
└── usage-stats.json          # 用量统计汇总
```

### 日志记录格式

每条记录包含以下字段：

| 字段 | 类型 | 说明 |
|------|------|------|
| **timestamp** | string | ISO 8601时间戳 |
| **call_id** | string | 唯一调用ID（格式：call-YYYYMMDD-NNN） |
| **input.query** | string | 搜索查询 |
| **input.parameters** | object | 调用参数 |
| **output.status** | string | 状态：success/failed |
| **output.result_count** | int | 返回结果数量 |
| **output.response_time_ms** | int | 响应时间（毫秒） |
| **output.error** | string | 错误信息（失败时） |
| **usage.daily_total** | int | 今日累计调用次数 |
| **usage.remaining** | int | 今日剩余额度 |

### 用量统计文件

`usage-stats.json` 维护累计统计数据：

```json
{
  "daily_usage": {
    "2026-03-09": {
      "total_calls": 15,
      "successful_calls": 14,
      "failed_calls": 1,
      "avg_response_time_ms": 1234,
      "daily_limit": 1000,
      "remaining": 985
    }
  },
  "monthly_summary": {
    "2026-03": {
      "total_calls": 450,
      "estimated_cost_yuan": 0
    }
  }
}
```

### 质量跟踪指标

#### 响应时间监控

- **正常范围**: < 2000ms
- **警告阈值**: 2000-5000ms
- **异常阈值**: > 5000ms

#### 成功率监控

- **正常**: > 95%
- **警告**: 90-95%
- **异常**: < 90%

#### 用量预警

- **正常**: remaining > 200
- **警告**: remaining 50-200
- **紧急**: remaining < 50

## 📊 计费说明

| 项目 | 说明 |
|------|------|
| **赠送额度** | 1000次/天 |
| **速率限制** | 3 QPS |
| **计费方式** | 按量后付费 |
| **价格** | 0.036元/次（网页/图像/视频） |

### 用量监控

- **实时查看**: 查看 `search-logs/usage-stats.json`
- **日志位置**: `search-logs/YYYY-MM-DD.jsonl`
- **建议**: 每日检查剩余额度，避免超出免费额度

### 成本估算

- 免费额度内：0元
- 超出后：每次调用约 0.036元
- 月度估算：`总调用次数 × 0.036元`

## ⚠️ 注意事项

### 1. 搜索日志记录（必须遵守）

**⚠️ 重要：每次调用前必须记录搜索日志**

**日志位置**: `search-logs/YYYY-MM-DD.jsonl`

**记录时机**:
- ✅ **调用前**：检查剩余额度，记录调用意图
- ✅ **调用后**：记录实际结果、响应时间、状态
- ❌ **异常时**：记录错误信息、错误码、重试建议

**忽略记录会导致**:
- 无法跟踪用量（可能超出免费额度）
- 无法监控质量（响应慢、失败率高等问题被忽视）
- 无法审计（调用历史不可追溯）

### 2. API Key安全
- ✅ 已配置在全局配置中，无需在代码中暴露
- ⚠️ 请勿将API Key提交到公开仓库

### 3. 调用限制
- **免费额度**: 1000次/天
- **速率限制**: 3 QPS
- **超出后**: 开始计费（0.036元/次）

### 4. 参数依赖
- `temperature`、`top_p` 仅在指定 `model` 时生效
- `resource_type_filter` 各类型独立计算 `top_k`

### 5. 超时处理
- **默认超时**: 15秒（配置中已设置）
- **建议**: 对于复杂查询，可适当增加超时时间

## 🔗 相关资源

- [百度千帆控制台](https://console.bce.baidu.com/qianfan/)
- [MCP配置文件](../opencode.json)
- [百度AI搜索文档](https://cloud.baidu.com/doc/qianfan/s/2mh4su4uy)

---

**维护者**: SEARCH-R Framework  
**更新时间**: 2026-03-09  
**MCP服务器**: aisearch-mcp-server  
**版本**: v1.1（新增搜索记录功能）
