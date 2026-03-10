#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
基层服务案例收集脚本

执行搜索任务，收集基层县公司、供电所的客户服务优秀案例
"""

import sys
import json
import time
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any

sys.path.insert(0, str(Path(__file__).parent))
from skills.baidu_web_search_api import BaiduWebSearch


SEARCH_ROUTES = {
    "route1_county": {
        "name": "县级供电公司客户服务创新案例",
        "keywords": [
            "县级供电公司 客户服务 创新 案例",
            "县供电公司 服务提升 先进经验",
            "县级供电企业 服务创新 做法"
        ]
    },
    "route2_station": {
        "name": "供电所优质服务典型案例",
        "keywords": [
            "供电所 优质服务 典型案例",
            "供电所 服务创新 先进经验",
            "供电所 零投诉 服务经验"
        ]
    },
    "route3_manager": {
        "name": "台区经理服务明星典型案例",
        "keywords": [
            "台区经理 服务明星 典型案例",
            "台区经理 客户服务 优秀案例",
            "网格经理 服务创新 先进经验"
        ]
    }
}


def extract_case_info(ref: Dict[str, Any], route_name: str) -> Dict[str, Any]:
    """
    从搜索结果中提取案例信息
    
    Args:
        ref: 搜索结果的单个引用
        route_name: 路线名称
        
    Returns:
        案例信息字典
    """
    case = {
        "案例标题": ref.get("title", ""),
        "单位名称": "",
        "服务对象": "",
        "服务模式": "",
        "创新点": "",
        "服务效果": "",
        "来源URL": ref.get("url", ""),
        "发布日期": ref.get("date", ""),
        "内容摘要": ref.get("content", "")[:500] if ref.get("content") else "",
        "相关度评分": ref.get("rerank_score", 0),
        "权威性评分": ref.get("authority_score", 0),
        "搜索路线": route_name,
        "采集时间": datetime.now().isoformat()
    }
    
    content = ref.get("content", "")
    title = ref.get("title", "")
    
    if "供电公司" in title or "供电公司" in content:
        import re
        match = re.search(r'([\u4e00-\u9fa5]+供电公司)', title + content)
        if match:
            case["单位名称"] = match.group(1)
    
    if "供电所" in title or "供电所" in content:
        import re
        match = re.search(r'([\u4e00-\u9fa5]+供电所)', title + content)
        if match:
            case["单位名称"] = match.group(1)
    
    if "台区经理" in title or "台区经理" in content:
        import re
        match = re.search(r'([\u4e00-\u9fa5]+台区经理)', title + content)
        if match:
            case["单位名称"] = match.group(1)
    
    return case


def deduplicate_cases(cases: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    去重案例列表
    
    Args:
        cases: 案例列表
        
    Returns:
        去重后的案例列表
    """
    seen_urls = set()
    seen_titles = set()
    unique_cases = []
    
    for case in cases:
        url = case.get("来源URL", "")
        title = case.get("案例标题", "")
        
        if url and url in seen_urls:
            continue
        
        normalized_title = title.lower().replace(" ", "").replace("-", "")
        if normalized_title in seen_titles:
            continue
        
        if url:
            seen_urls.add(url)
        seen_titles.add(normalized_title)
        unique_cases.append(case)
    
    return unique_cases


def main():
    """执行搜索任务主函数"""
    print("=" * 80)
    print("基层服务案例收集任务开始")
    print("=" * 80)
    print()
    
    client = BaiduWebSearch()
    
    output_dir = Path(__file__).parent / "search-results"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    all_results = {}
    all_cases = []
    
    for route_key, route_info in SEARCH_ROUTES.items():
        route_name = route_info["name"]
        keywords = route_info["keywords"]
        
        print(f"\n{'='*80}")
        print(f"搜索路线: {route_name}")
        print(f"{'='*80}")
        
        route_cases = []
        
        for i, keyword in enumerate(keywords, 1):
            print(f"\n[{i}/{len(keywords)}] 搜索关键词: {keyword}")
            
            result = client.search(
                query=keyword,
                top_k=15,
                resource_types=["web"],
                recency_filter="year"
            )
            
            if result["success"]:
                references = result.get("references", [])
                print(f"  ✓ 获取 {len(references)} 条结果 (耗时: {result['response_time_ms']}ms)")
                
                for ref in references:
                    case = extract_case_info(ref, route_name)
                    route_cases.append(case)
                
                time.sleep(1)
            else:
                print(f"  ✗ 搜索失败: {result.get('error', 'Unknown error')}")
        
        route_cases = deduplicate_cases(route_cases)
        all_results[route_key] = {
            "route_name": route_name,
            "keywords": keywords,
            "total_cases": len(route_cases),
            "cases": route_cases
        }
        all_cases.extend(route_cases)
        
        print(f"\n路线汇总: {route_name}")
        print(f"  去重后案例数: {len(route_cases)}")
    
    all_cases = deduplicate_cases(all_cases)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    county_file = output_dir / "county_level_cases.json"
    with open(county_file, 'w', encoding='utf-8') as f:
        json.dump(all_results["route1_county"], f, ensure_ascii=False, indent=2)
    print(f"\n✓ 保存县级公司案例: {county_file}")
    
    station_file = output_dir / "power_station_cases.json"
    with open(station_file, 'w', encoding='utf-8') as f:
        json.dump(all_results["route2_station"], f, ensure_ascii=False, indent=2)
    print(f"✓ 保存供电所案例: {station_file}")
    
    manager_file = output_dir / "area_manager_cases.json"
    with open(manager_file, 'w', encoding='utf-8') as f:
        json.dump(all_results["route3_manager"], f, ensure_ascii=False, indent=2)
    print(f"✓ 保存台区经理案例: {manager_file}")
    
    summary = {
        "采集时间": datetime.now().isoformat(),
        "搜索统计": {
            "路线1_县级公司": {
                "关键词数量": len(SEARCH_ROUTES["route1_county"]["keywords"]),
                "案例数量": len(all_results["route1_county"]["cases"])
            },
            "路线2_供电所": {
                "关键词数量": len(SEARCH_ROUTES["route2_station"]["keywords"]),
                "案例数量": len(all_results["route2_station"]["cases"])
            },
            "路线3_台区经理": {
                "关键词数量": len(SEARCH_ROUTES["route3_manager"]["keywords"]),
                "案例数量": len(all_results["route3_manager"]["cases"])
            },
            "总计案例数": len(all_cases),
            "去重后案例数": len(all_cases)
        },
        "案例列表": [
            {
                "序号": i+1,
                "标题": case["案例标题"],
                "单位": case["单位名称"],
                "路线": case["搜索路线"],
                "相关度": f"{case['相关度评分']:.2f}" if case.get('相关度评分') else "N/A",
                "日期": case["发布日期"],
                "URL": case["来源URL"]
            }
            for i, case in enumerate(all_cases)
        ]
    }
    
    summary_file = output_dir / "all_cases_summary.json"
    with open(summary_file, 'w', encoding='utf-8') as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)
    print(f"✓ 保存汇总结果: {summary_file}")
    
    print("\n" + "="*80)
    print("搜索统计")
    print("="*80)
    print(f"路线1 - 县级供电公司客户服务创新案例: {len(all_results['route1_county']['cases'])} 个案例")
    print(f"路线2 - 供电所优质服务典型案例: {len(all_results['route2_station']['cases'])} 个案例")
    print(f"路线3 - 台区经理服务明星典型案例: {len(all_results['route3_manager']['cases'])} 个案例")
    print(f"\n总计案例数量: {len(all_cases)} 个")
    print("="*80)
    print("\n任务完成！")


if __name__ == "__main__":
    main()
