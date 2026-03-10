#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
基层服务案例搜索脚本

三路并行搜索：
1. 县级供电公司客户服务创新案例
2. 供电所优质服务典型案例
3. 台区经理服务明星典型案例

目标：新增30-50个基层服务案例
"""

import sys
import json
import time
from pathlib import Path
from datetime import datetime

# 导入百度搜索API
sys.path.insert(0, str(Path(__file__).parent / "skills"))
from baidu_web_search_api import BaiduWebSearch


def search_county_level_cases(client: BaiduWebSearch, output_dir: Path):
    """搜索县级供电公司客户服务创新案例"""
    print("\n" + "="*60)
    print("路线1：县级供电公司客户服务创新案例")
    print("="*60)
    
    queries = [
        "县级供电公司 客户服务 创新 案例",
        "县级供电公司 优质服务 典型案例",
        "县供电公司 服务提升 先进经验",
        "县级供电企业 服务创新 做法",
        "县供电公司 营商环境 优化 案例"
    ]
    
    all_results = []
    
    for i, query in enumerate(queries, 1):
        print(f"\n[{i}/{len(queries)}] 搜索: {query}")
        
        result = client.search(
            query=query,
            top_k=15,
            resource_types=["web"],
            recency_filter="year"  # 最近一年
        )
        
        if result["success"]:
            print(f"  ✓ 成功获取 {result['result_count']} 条结果")
            all_results.extend(result["references"])
        else:
            print(f"  ✗ 搜索失败: {result.get('error', 'Unknown error')}")
        
        time.sleep(1)  # 避免频繁请求
    
    # 保存结果
    output_file = output_dir / "county_level_cases.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(all_results, f, ensure_ascii=False, indent=2)
    
    print(f"\n✓ 路线1完成，共获取 {len(all_results)} 条结果")
    print(f"  保存至: {output_file}")
    
    return all_results


def search_power_station_cases(client: BaiduWebSearch, output_dir: Path):
    """搜索供电所优质服务典型案例"""
    print("\n" + "="*60)
    print("路线2：供电所优质服务典型案例")
    print("="*60)
    
    queries = [
        "供电所 优质服务 典型案例",
        "供电所 服务创新 先进经验",
        "供电所 客户服务 优秀案例",
        "基层供电所 服务提升 做法",
        "供电所 零投诉 服务经验"
    ]
    
    all_results = []
    
    for i, query in enumerate(queries, 1):
        print(f"\n[{i}/{len(queries)}] 搜索: {query}")
        
        result = client.search(
            query=query,
            top_k=15,
            resource_types=["web"],
            recency_filter="year"
        )
        
        if result["success"]:
            print(f"  ✓ 成功获取 {result['result_count']} 条结果")
            all_results.extend(result["references"])
        else:
            print(f"  ✗ 搜索失败: {result.get('error', 'Unknown error')}")
        
        time.sleep(1)
    
    # 保存结果
    output_file = output_dir / "power_station_cases.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(all_results, f, ensure_ascii=False, indent=2)
    
    print(f"\n✓ 路线2完成，共获取 {len(all_results)} 条结果")
    print(f"  保存至: {output_file}")
    
    return all_results


def search_area_manager_cases(client: BaiduWebSearch, output_dir: Path):
    """搜索台区经理服务明星典型案例"""
    print("\n" + "="*60)
    print("路线3：台区经理服务明星典型案例")
    print("="*60)
    
    queries = [
        "台区经理 服务明星 典型案例",
        "台区经理 客户服务 优秀案例",
        "网格经理 服务创新 先进经验",
        "台区经理 优质服务 做法",
        "客户经理 服务明星 典型"
    ]
    
    all_results = []
    
    for i, query in enumerate(queries, 1):
        print(f"\n[{i}/{len(queries)}] 搜索: {query}")
        
        result = client.search(
            query=query,
            top_k=15,
            resource_types=["web"],
            recency_filter="year"
        )
        
        if result["success"]:
            print(f"  ✓ 成功获取 {result['result_count']} 条结果")
            all_results.extend(result["references"])
        else:
            print(f"  ✗ 搜索失败: {result.get('error', 'Unknown error')}")
        
        time.sleep(1)
    
    # 保存结果
    output_file = output_dir / "area_manager_cases.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(all_results, f, ensure_ascii=False, indent=2)
    
    print(f"\n✓ 路线3完成，共获取 {len(all_results)} 条结果")
    print(f"  保存至: {output_file}")
    
    return all_results


def main():
    """主函数"""
    print("="*60)
    print("基层服务案例三路并行搜索")
    print("="*60)
    print(f"开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 创建输出目录
    output_dir = Path(__file__).parent / "search-results"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # 创建搜索客户端
    try:
        client = BaiduWebSearch()
        print("✓ 百度搜索客户端初始化成功")
    except Exception as e:
        print(f"✗ 百度搜索客户端初始化失败: {e}")
        return
    
    # 执行三路并行搜索
    all_results = {}
    
    # 路线1：县级供电公司
    county_results = search_county_level_cases(client, output_dir)
    all_results["county_level"] = county_results
    
    # 路线2：供电所
    station_results = search_power_station_cases(client, output_dir)
    all_results["power_station"] = station_results
    
    # 路线3：台区经理
    manager_results = search_area_manager_cases(client, output_dir)
    all_results["area_manager"] = manager_results
    
    # 统计总结果
    total_count = sum(len(results) for results in all_results.values())
    
    # 保存汇总结果
    summary_file = output_dir / "all_cases_summary.json"
    with open(summary_file, 'w', encoding='utf-8') as f:
        json.dump({
            "search_time": datetime.now().isoformat(),
            "total_count": total_count,
            "route_counts": {
                "county_level": len(all_results["county_level"]),
                "power_station": len(all_results["power_station"]),
                "area_manager": len(all_results["area_manager"])
            },
            "results": all_results
        }, f, ensure_ascii=False, indent=2)
    
    # 输出总结
    print("\n" + "="*60)
    print("搜索完成总结")
    print("="*60)
    print(f"路线1（县级公司）: {len(all_results['county_level'])} 条")
    print(f"路线2（供电所）: {len(all_results['power_station'])} 条")
    print(f"路线3（台区经理）: {len(all_results['area_manager'])} 条")
    print(f"总计: {total_count} 条结果")
    print(f"\n结果保存至: {output_dir}")
    print(f"结束时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")


if __name__ == "__main__":
    main()
