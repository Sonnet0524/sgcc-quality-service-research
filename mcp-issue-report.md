---
issue: MCP工具不可用问题记录
date: 2026-03-10
status: open
priority: high
---

# MCP工具不可用问题记录

## 📋 问题概述

**问题描述**：在当前会话中，百度AI搜索MCP工具（AIsearch）不可用

**发现时间**：2026-03-10

**影响范围**：无法使用AIsearch工具进行智能搜索，需要使用webfetch作为备选方案

---

## 🔍 问题描述

### 预期行为

根据配置文件 `Opencode.json`，MCP服务器应该已配置并可用：

```json
{
  "mcp": {
    "aisearch-mcp-server": {
      "type": "remote",
      "url": "https://qianfan.baidubce.com/v2/ai_search/mcp",
      "headers": {
        "Authorization": "Bearer ${BAIDU_AISEARCH_TOKEN}"
      },
      "enabled": true,
      "timeout": 15000
    }
  }
}
```

**预期**：应该能够在工具列表中看到AIsearch工具，并可以调用。

### 实际行为

**现象1：工具列表中无AIsearch工具**
- 我的可用工具列表：bash, read, write, edit, glob, grep, webfetch, task, todowrite, skill
- MCP工具（如AIsearch）不在列表中

**现象2：Skill工具无法加载skill**
```
Error: Skill "baidu-search" not found. Available skills: 0
```

**现象3：通过Task启动子Agent调用时报告不可用**
- 子Agent报告："AIsearch MCP工具不可用"
- 子Agent使用webfetch作为备选方案

---

## 🔧 尝试的诊断方法

### 方法1：检查配置文件

**检查内容**：
- ✅ `Opencode.json` 配置正确
- ✅ MCP服务器已启用（`enabled: true`）
- ✅ URL正确：`https://qianfan.baidubce.com/v2/ai_search/mcp`
- ✅ Token配置：`Bearer ${BAIDU_AISEARCH_TOKEN}`

**结果**：配置文件正常

### 方法2：检查Token

**检查内容**：
- ✅ Token文件存在：`D:/opencode/github/.env.local`
- ✅ Token格式正确：`bce-v3/ALTAK-...`（已配置）

**结果**：Token配置正常

### 方法3：尝试加载Skill

**操作**：
```
skill(name="baidu-search")
```

**结果**：
```
Error: Skill "baidu-search" not found. Available skills: 0
```

**分析**：Skill加载机制可能未工作

### 方法4：尝试直接调用API

**操作**：创建Python脚本 `baidu_search_api.py` 直接调用API

**结果**：
```json
{
  "jsonrpc": "2.0",
  "id": null,
  "error": {
    "code": -32600,
    "message": "Invalid JSON-RPC version"
  }
}
```

**分析**：
- API端点需要特定的JSON-RPC格式
- 直接HTTP调用可能不是正确方式
- 应该通过MCP协议调用

### 方法5：检查SEARCH-R仓库

**检查内容**：
- ✅ SEARCH-R仓库存在：`/d/opencode/github/SEARCH-R`
- ✅ Skills文件存在：`baidu-search.md`等
- ✅ 配置文件相同

**结果**：SEARCH-R仓库配置一致，说明配置应该正确

---

## 🎯 可能的原因分析

### 原因1：会话启动时MCP未加载

**可能性**：⭐⭐⭐⭐⭐ （最可能）

**分析**：
- MCP服务器需要在会话启动时加载
- 如果会话启动时加载失败，整个会话中都不可用
- 配置文件正确，但工具未注入到工具列表

**验证方法**：
- 重启会话，观察MCP工具是否出现
- 检查会话启动日志

### 原因2：环境变量未传递

**可能性**：⭐⭐⭐⭐

**分析**：
- Token通过环境变量 `${BAIDU_AISEARCH_TOKEN}` 引用
- 如果环境变量未正确传递，MCP服务器可能初始化失败
- 但不影响配置文件的正确性

**验证方法**：
- 检查环境变量是否正确设置
- 尝试硬编码Token（不推荐）

### 原因3：MCP服务器连接失败

**可能性**：⭐⭐⭐

**分析**：
- MCP服务器是远程服务：`https://qianfan.baidubce.com/v2/ai_search/mcp`
- 网络问题或服务器问题可能导致连接失败
- 但这应该在会话启动时就报错

**验证方法**：
- 测试网络连接
- 检查百度千帆服务状态

### 原因4：Opencode框架问题

**可能性**：⭐⭐

**分析**：
- Opencode框架可能存在bug
- MCP工具注入机制可能异常
- 但这应该是框架层面的问题

**验证方法**：
- 检查Opencode版本
- 查看框架日志

---

## 📊 对比分析

### 昨天 vs 今天

| 项目 | 昨天 | 今天 |
|------|------|------|
| MCP工具状态 | ✅ 可用 | ❌ 不可用 |
| 配置文件 | ✅ 正确 | ✅ 正确 |
| Token | ✅ 正确 | ✅ 正确 |
| 会话状态 | - | 新会话 |

**关键差异**：会话不同，可能是会话启动时MCP加载失败

---

## 🔨 解决方案建议

### 方案1：重启会话（推荐）

**操作步骤**：
1. 退出当前会话
2. 重新启动会话
3. 检查工具列表中是否有AIsearch工具
4. 如果出现，则问题解决

**预期效果**：MCP工具应该重新加载并可用

### 方案2：检查会话启动日志

**操作步骤**：
1. 查看Opencode启动日志
2. 检查MCP服务器初始化是否成功
3. 如果有错误，根据错误信息修复

**预期效果**：定位具体原因

### 方案3：使用webfetch备选方案（临时）

**当前状态**：✅ 已实施

**效果**：
- 成功收集19个案例
- 搜索日志正常记录
- 用量统计正常维护

**限制**：
- 搜索效率较低
- 无法进行AI智能总结
- 需要多次访问不同网站

### 方案4：联系技术支持

**操作步骤**：
1. 提供本故障报告
2. 提供会话ID或日志
3. 等待技术支持反馈

**预期效果**：获得根本解决方案

---

## 📝 相关文件

### 配置文件
- `D:\opencode\github\sgcc-quality-service-research\Opencode.json`
- `D:\opencode\github\.env.local`

### Skill文档
- `D:\opencode\github\sgcc-quality-service-research\skills\baidu-search.md`
- `D:\opencode\github\SEARCH-R\agents\research\skills\baidu-search.md`

### 尝试实现
- `D:\opencode\github\sgcc-quality-service-research\skills\baidu_search_api.py`

### 搜索日志
- `D:\opencode\github\sgcc-quality-service-research\search-logs\2026-03-10.jsonl`
- `D:\opencode\github\sgcc-quality-service-research\search-logs\usage-stats.json`

---

## 🎓 经验总结

### 教训1：会话依赖性

**认识**：MCP工具是会话级别的，需要在会话启动时加载

**建议**：每次新会话都应检查MCP工具是否可用

### 教训2：备选方案的重要性

**认识**：即使MCP工具不可用，也应该有备选方案

**建议**：始终保持webfetch等其他工具的可用性

### 教训3：详细的错误记录

**认识**：详细的错误记录有助于问题诊断

**建议**：记录所有尝试的方法和结果

---

## 📈 后续行动

### 立即行动
- [x] 创建本故障报告
- [ ] 重启会话测试MCP工具
- [ ] 记录重启后的状态

### 短期行动
- [ ] 分析会话启动日志
- [ ] 优化MCP加载流程
- [ ] 建立MCP可用性检查机制

### 长期行动
- [ ] 完善故障排查文档
- [ ] 建立自动恢复机制
- [ ] 优化备选方案

---

## 💬 反馈

### 给用户的建议

1. **重启会话**：最可能解决问题的方式
2. **检查启动日志**：查看是否有MCP加载错误
3. **继续使用webfetch**：临时可用的备选方案

### 给开发者的建议

1. **增加MCP状态指示**：明确显示MCP工具是否加载成功
2. **提供重新加载机制**：允许会话中重新加载MCP工具
3. **改进错误提示**：当MCP不可用时给出明确提示

---

**报告人**: Research Agent  
**报告时间**: 2026-03-10 15:30  
**文件位置**: `D:\opencode\github\sgcc-quality-service-research\mcp-issue-report.md`  
**状态**: Open - 等待重启会话测试
