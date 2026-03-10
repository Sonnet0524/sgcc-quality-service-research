#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
百度AI搜索API调用脚本

功能：
1. 调用百度AI搜索API进行搜索
2. 自动记录搜索日志
3. 维护用量统计
4. 支持基础搜索和AI搜索

使用方法：
    python baidu_search_api.py --query "搜索关键词"
    python baidu_search_api.py --query "搜索关键词" --model "ERNIE-3.5-8K" --temperature 0.3
"""

import os
import sys
import json
import time
import argparse
import requests
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, List


class BaiduAISearch:
    """百度AI搜索客户端"""
    
    def __init__(self, token: Optional[str] = None):
        """
        初始化搜索客户端
        
        Args:
            token: 百度AI搜索Token，如果为None则从环境变量或配置文件读取
        """
        self.token = token or self._load_token()
        self.base_url = "https://qianfan.baidubce.com/v2/ai_search/mcp"
        self.timeout = 15
        
        # 搜索日志目录
        self.log_dir = Path(__file__).parent.parent / "search-logs"
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        # 今日日期
        self.today = datetime.now().strftime("%Y-%m-%d")
        
    def _load_token(self) -> str:
        """从环境变量或配置文件加载Token"""
        # 尝试从环境变量加载
        token = os.getenv("BAIDU_AISEARCH_TOKEN")
        if token:
            return token
            
        # 尝试从配置文件加载（项目根目录的上级目录）
        env_file = Path(__file__).parent.parent.parent / ".env.local"
        if env_file.exists():
            with open(env_file, 'r', encoding='utf-8') as f:
                for line in f:
                    if line.startswith("BAIDU_AISEARCH_TOKEN="):
                        return line.split('=', 1)[1].strip()
        
        raise ValueError("未找到BAIDU_AISEARCH_TOKEN，请设置环境变量或在.env.local文件中配置")
    
    def _get_call_id(self) -> str:
        """生成唯一调用ID"""
        # 读取今日已有的调用次数
        stats = self._load_usage_stats()
        daily_usage = stats.get("daily_usage", {}).get(self.today, {})
        total_calls = daily_usage.get("total_calls", 0)
        return f"call-{self.today.replace('-', '')}-{total_calls + 1:03d}"
    
    def _load_usage_stats(self) -> Dict:
        """加载用量统计"""
        stats_file = self.log_dir / "usage-stats.json"
        if stats_file.exists():
            with open(stats_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            return {
                "daily_usage": {},
                "monthly_summary": {}
            }
    
    def _save_usage_stats(self, stats: Dict):
        """保存用量统计"""
        stats_file = self.log_dir / "usage-stats.json"
        with open(stats_file, 'w', encoding='utf-8') as f:
            json.dump(stats, f, ensure_ascii=False, indent=2)
    
    def _log_search(self, log_entry: Dict):
        """记录搜索日志"""
        log_file = self.log_dir / f"{self.today}.jsonl"
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(log_entry, ensure_ascii=False) + '\n')
    
    def _update_usage_stats(self, success: bool, response_time_ms: int):
        """更新用量统计"""
        stats = self._load_usage_stats()
        
        # 初始化今日统计
        if self.today not in stats["daily_usage"]:
            stats["daily_usage"][self.today] = {
                "total_calls": 0,
                "successful_calls": 0,
                "failed_calls": 0,
                "avg_response_time_ms": 0,
                "daily_limit": 1000,
                "remaining": 1000
            }
        
        daily = stats["daily_usage"][self.today]
        daily["total_calls"] += 1
        if success:
            daily["successful_calls"] += 1
        else:
            daily["failed_calls"] += 1
        
        # 更新平均响应时间
        prev_avg = daily["avg_response_time_ms"]
        prev_count = daily["total_calls"] - 1
        if prev_count > 0:
            daily["avg_response_time_ms"] = int((prev_avg * prev_count + response_time_ms) / daily["total_calls"])
        else:
            daily["avg_response_time_ms"] = response_time_ms
        
        # 更新剩余额度（假设每次调用消耗1次）
        daily["remaining"] = daily["daily_limit"] - daily["total_calls"]
        
        # 更新月度统计
        month = self.today[:7]
        if month not in stats["monthly_summary"]:
            stats["monthly_summary"][month] = {
                "total_calls": 0,
                "estimated_cost_yuan": 0
            }
        stats["monthly_summary"][month]["total_calls"] += 1
        
        self._save_usage_stats(stats)
        return daily["remaining"]
    
    def search(
        self,
        query: str,
        model: Optional[str] = None,
        instruction: Optional[str] = None,
        temperature: Optional[float] = None,
        resource_type_filter: Optional[List[Dict]] = None
    ) -> Dict[str, Any]:
        """
        执行搜索
        
        Args:
            query: 搜索查询关键词
            model: 大模型名称（如ERNIE-3.5-8K），不指定则返回原始结果
            instruction: 控制搜索结果输出风格和格式
            temperature: 模型输出随机性
            resource_type_filter: 资源类型和返回数量
            
        Returns:
            搜索结果字典
        """
        call_id = self._get_call_id()
        timestamp_start = datetime.now()
        
        # 构建请求参数
        # 尝试两种格式：直接API格式和MCP协议格式
        
        # 方式1：直接API格式
        api_params: Dict[str, Any] = {
            "query": query
        }
        
        # 添加可选参数
        if model:
            api_params["model"] = model
        if instruction:
            api_params["instruction"] = instruction
        if temperature is not None:
            api_params["temperature"] = temperature
        if resource_type_filter:
            api_params["resource_type_filter"] = resource_type_filter
        
        # 记录调用前日志
        stats = self._load_usage_stats()
        daily_usage = stats.get("daily_usage", {}).get(self.today, {})
        
        log_before = {
            "timestamp": timestamp_start.isoformat() + "Z",
            "call_id": call_id,
            "phase": "before",
            "input": {
                "query": query,
                "parameters": api_params
            },
            "usage_before": {
                "daily_total": daily_usage.get("total_calls", 0),
                "daily_limit": daily_usage.get("daily_limit", 1000),
                "remaining": daily_usage.get("remaining", 1000)
            }
        }
        self._log_search(log_before)
        self._log_search(log_before)
        
        # 执行搜索
        start_time = time.time()
        try:
            headers = {
                "Authorization": f"Bearer {self.token}",
                "Content-Type": "application/json"
            }
            
            start_time = time.time()
            response = requests.post(
                self.base_url,
                headers=headers,
                json=api_params,
                timeout=self.timeout
            )
            end_time = time.time()
            response_time_ms = int((end_time - start_time) * 1000)
            
            # 检查响应状态
            if response.status_code == 200:
                result = response.json()
                
                # 处理MCP协议响应
                if "result" in result:
                    result = result["result"]
                    success = True
                elif "error" in result:
                    success = False
                    error = result["error"]
                    result = {
                        "success": False,
                        "error": error.get("message", str(error)),
                        "error_code": error.get("code", "UNKNOWN")
                    }
                else:
                    success = True
                
                # 记录成功日志
                result_count = len(result.get("results", result.get("content", [])))
                log_after = {
                    "timestamp": datetime.now().isoformat() + "Z",
                    "call_id": call_id,
                    "phase": "after",
                    "output": {
                        "status": "success",
                        "result_count": result_count,
                        "response_time_ms": response_time_ms,
                        "request_id": result.get("request_id", "")
                    },
                    "results_preview": result.get("results", result.get("content", []))[:3],  # 只记录前3个结果
                    "usage_after": {}
                }
                
            else:
                success = False
                error_data = response.json() if response.headers.get('content-type', '').startswith('application/json') else {}
                
                # 记录失败日志
                log_after = {
                    "timestamp": datetime.now().isoformat() + "Z",
                    "call_id": call_id,
                    "phase": "after",
                    "output": {
                        "status": "failed",
                        "error_code": response.status_code,
                        "error_message": error_data.get("error_msg", response.text),
                        "response_time_ms": response_time_ms
                    },
                    "retry_suggestion": self._get_retry_suggestion(response.status_code),
                    "usage_after": {}
                }
                
                result = {
                    "success": False,
                    "error": error_data.get("error_msg", f"HTTP {response.status_code}"),
                    "status_code": response.status_code
                }
        
        except Exception as e:
            success = False
            # 计算响应时间（如果start_time已定义）
            try:
                response_time_ms = int((time.time() - start_time) * 1000)
            except NameError:
                response_time_ms = 0
            
            # 记录异常日志
            log_after = {
                "timestamp": datetime.now().isoformat() + "Z",
                "call_id": call_id,
                "phase": "after",
                "output": {
                    "status": "failed",
                    "error_code": "EXCEPTION",
                    "error_message": str(e),
                    "response_time_ms": response_time_ms
                },
                "retry_suggestion": "检查网络连接或API配置",
                "usage_after": {}
            }
            
            result = {
                "success": False,
                "error": str(e),
                "status_code": "EXCEPTION"
            }
        
        # 更新用量统计
        remaining = self._update_usage_stats(success, response_time_ms)
        log_after["usage_after"]["remaining"] = remaining
        
        # 记录调用后日志
        self._log_search(log_after)
        
        # 添加用量信息到结果
        result["usage"] = {
            "daily_total": daily_usage.get("total_calls", 0) + 1,
            "remaining": remaining
        }
        
        return result
    
    def _get_retry_suggestion(self, status_code: int) -> str:
        """根据错误码返回重试建议"""
        suggestions = {
            401: "检查API Token是否正确",
            403: "检查API权限配置",
            429: "请求过于频繁，请稍后重试",
            500: "服务器错误，请稍后重试",
            503: "服务暂时不可用，请稍后重试"
        }
        return suggestions.get(status_code, "请检查请求参数或联系技术支持")


def main():
    """命令行入口"""
    parser = argparse.ArgumentParser(description="百度AI搜索API调用工具")
    parser.add_argument("--query", "-q", required=True, help="搜索查询关键词")
    parser.add_argument("--model", "-m", default=None, help="大模型名称（如ERNIE-3.5-8K）")
    parser.add_argument("--instruction", "-i", default=None, help="输出格式指令")
    parser.add_argument("--temperature", "-t", type=float, default=None, help="模型温度参数")
    parser.add_argument("--top-k", "-k", type=int, default=5, help="返回结果数量")
    parser.add_argument("--output", "-o", default=None, help="输出文件路径")
    
    args = parser.parse_args()
    
    # 创建搜索客户端
    client = BaiduAISearch()
    
    # 执行搜索
    print(f"正在搜索: {args.query}")
    result = client.search(
        query=args.query,
        model=args.model,
        instruction=args.instruction,
        temperature=args.temperature,
        resource_type_filter=[{"type": "web", "top_k": args.top_k}]
    )
    
    # 输出结果
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        print(f"结果已保存到: {args.output}")
    else:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    
    # 打印用量信息
    if "usage" in result:
        print(f"\n今日用量: {result['usage']['daily_total']} 次")
        print(f"剩余额度: {result['usage']['remaining']} 次")


if __name__ == "__main__":
    main()
