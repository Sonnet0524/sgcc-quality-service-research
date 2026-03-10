#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
从搜索结果中提取案例信息

功能：
1. 读取搜索结果JSON文件
2. 提取关键案例信息
3. 去重和过滤
4. 生成案例数据库
"""

import json
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any


def extract_case_info(item: Dict[str, Any], source_type: str) -> Dict[str, Any]:
    """
    从搜索结果中提取案例信息
    
    Args:
        item: 搜索结果项
        source_type: 来源类型（county_level/power_station/area_manager）
    
    Returns:
        案例信息字典
    """
    title = item.get("title", "")
    content = item.get("content", "") or item.get("snippet", "")
    url = item.get("url", "")
    date = item.get("date", "")
    website = item.get("website", "")
    
    # 提取单位名称
    unit_patterns = [
        r"国网(.{2,10}?供电公司)",
        r"国网(.{2,10}?供电局)",
        r"(.{2,10}?供电所)",
        r"(.{2,10}?供电站)",
    ]
    
    unit_name = ""
    for pattern in unit_patterns:
        match = re.search(pattern, title)
        if match:
            unit_name = match.group(0)
            break
    
    # 如果标题中没有，从内容中提取
    if not unit_name:
        for pattern in unit_patterns:
            match = re.search(pattern, content[:200])
            if match:
                unit_name = match.group(0)
                break
    
    # 提取服务对象
    service_objects = []
    object_keywords = ["居民", "企业", "农户", "商户", "用户", "客户"]
    for keyword in object_keywords:
        if keyword in content:
            service_objects.append(keyword)
    
    # 提取创新关键词
    innovation_keywords = [
        "主动服务", "上门服务", "网格化", "一站式", "零距离",
        "快速响应", "智慧", "智能", "数字化", "创新",
        "贴心服务", "优质服务", "满意服务", "便民服务"
    ]
    
    found_innovations = []
    for keyword in innovation_keywords:
        if keyword in title or keyword in content:
            found_innovations.append(keyword)
    
    # 提取效果关键词
    effect_keywords = [
        "提升", "压缩", "缩短", "降低", "节省", "节约",
        "满意度", "效率", "质量", "便利"
    ]
    
    found_effects = []
    for keyword in effect_keywords:
        if keyword in content:
            found_effects.append(keyword)
    
    return {
        "title": title,
        "unit_name": unit_name,
        "source_type": source_type,
        "date": date,
        "website": website,
        "url": url,
        "service_objects": service_objects[:3] if service_objects else ["未明确"],
        "innovation_keywords": found_innovations[:5],
        "effect_keywords": found_effects[:5],
        "content_length": len(content),
        "content_preview": content[:300] + "..." if len(content) > 300 else content,
        "full_content": content
    }


def process_search_results(input_dir: Path, output_dir: Path):
    """
    处理搜索结果
    
    Args:
        input_dir: 输入目录
        output_dir: 输出目录
    """
    print("="*60)
    print("案例提取与整理")
    print("="*60)
    
    # 读取搜索结果
    files = {
        "county_level": input_dir / "county_level_cases.json",
        "power_station": input_dir / "power_station_cases.json",
        "area_manager": input_dir / "area_manager_cases.json"
    }
    
    all_cases = []
    case_urls = set()  # 用于去重
    
    for source_type, file_path in files.items():
        if not file_path.exists():
            print(f"⚠️  文件不存在: {file_path}")
            continue
        
        print(f"\n处理: {source_type}")
        
        with open(file_path, 'r', encoding='utf-8') as f:
            results = json.load(f)
        
        extracted_count = 0
        for item in results:
            # 去重
            url = item.get("url", "")
            if url in case_urls:
                continue
            
            # 提取案例信息
            case_info = extract_case_info(item, source_type)
            
            # 过滤无效案例
            if not case_info["title"] or len(case_info["full_content"]) < 100:
                continue
            
            # 添加到列表
            all_cases.append(case_info)
            case_urls.add(url)
            extracted_count += 1
        
        print(f"  ✓ 提取 {extracted_count} 个案例")
    
    print(f"\n{'='*60}")
    print(f"总计提取: {len(all_cases)} 个案例")
    
    # 按来源类型统计
    type_counts = {}
    for case in all_cases:
        source_type = case["source_type"]
        type_counts[source_type] = type_counts.get(source_type, 0) + 1
    
    print("\n案例类型分布:")
    for source_type, count in type_counts.items():
        print(f"  {source_type}: {count} 个")
    
    # 保存结果
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # 保存完整案例库
    output_file = output_dir / "cases_database.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump({
            "extract_time": datetime.now().isoformat(),
            "total_count": len(all_cases),
            "type_counts": type_counts,
            "cases": all_cases
        }, f, ensure_ascii=False, indent=2)
    
    print(f"\n✓ 案例数据库已保存: {output_file}")
    
    # 生成简要列表
    summary_file = output_dir / "cases_summary.md"
    with open(summary_file, 'w', encoding='utf-8') as f:
        f.write("# 基层服务案例库\n\n")
        f.write(f"**提取时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write(f"**案例总数**: {len(all_cases)} 个\n\n")
        f.write("## 案例类型分布\n\n")
        for source_type, count in type_counts.items():
            f.write(f"- {source_type}: {count} 个\n")
        
        f.write("\n## 案例列表\n\n")
        
        # 按类型分组
        for source_type in ["county_level", "power_station", "area_manager"]:
            cases_of_type = [c for c in all_cases if c["source_type"] == source_type]
            if not cases_of_type:
                continue
            
            f.write(f"\n### {source_type} ({len(cases_of_type)} 个)\n\n")
            
            for i, case in enumerate(cases_of_type, 1):
                f.write(f"#### 案例 {i}: {case['title']}\n\n")
                f.write(f"- **单位**: {case['unit_name'] or '未明确'}\n")
                f.write(f"- **日期**: {case['date']}\n")
                f.write(f"- **来源**: {case['website']}\n")
                if case['innovation_keywords']:
                    f.write(f"- **创新点**: {', '.join(case['innovation_keywords'])}\n")
                if case['effect_keywords']:
                    f.write(f"- **效果**: {', '.join(case['effect_keywords'])}\n")
                f.write(f"- **内容预览**: {case['content_preview']}\n\n")
    
    print(f"✓ 案例摘要已保存: {summary_file}")
    
    return all_cases


def main():
    """主函数"""
    input_dir = Path(__file__).parent / "search-results"
    output_dir = Path(__file__).parent / "cases-database"
    
    cases = process_search_results(input_dir, output_dir)
    
    print(f"\n{'='*60}")
    print("案例提取完成！")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
