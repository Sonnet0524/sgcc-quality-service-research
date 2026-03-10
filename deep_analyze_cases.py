#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
案例深度分析脚本

功能：
1. 筛选典型案例（30-40个）
2. 对每个案例进行深度分析：
   - 做法分析
   - 优势分析
   - 劣势分析
   - 武侯应用分析（可能性、问题、方法、建议）
3. 生成深度分析报告
"""

import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any


def select_typical_cases(cases: List[Dict], max_cases: int = 35) -> List[Dict]:
    """
    筛选典型案例
    
    选择标准：
    1. 内容丰富度（content_length）
    2. 创新点数量（innovation_keywords）
    3. 效果关键词数量（effect_keywords）
    4. 覆盖不同类型和地区
    """
    # 评分
    for case in cases:
        score = 0
        
        # 内容丰富度
        content_len = case.get("content_length", 0)
        if content_len > 1000:
            score += 30
        elif content_len > 500:
            score += 20
        elif content_len > 300:
            score += 10
        
        # 创新点数量
        innovations = case.get("innovation_keywords", [])
        score += len(innovations) * 10
        
        # 效果关键词数量
        effects = case.get("effect_keywords", [])
        score += len(effects) * 5
        
        case["score"] = score
    
    # 排序
    sorted_cases = sorted(cases, key=lambda x: x["score"], reverse=True)
    
    # 选择前N个案例
    selected_cases = sorted_cases[:max_cases]
    
    # 确保类型平衡
    type_counts = {}
    for case in selected_cases:
        source_type = case["source_type"]
        type_counts[source_type] = type_counts.get(source_type, 0) + 1
    
    # 如果某类型案例过少，补充
    min_per_type = max_cases // 3 - 2
    for source_type in ["county_level", "power_station", "area_manager"]:
        if type_counts.get(source_type, 0) < min_per_type:
            # 从剩余案例中补充该类型
            remaining = [c for c in sorted_cases[max_cases:] if c["source_type"] == source_type]
            needed = min_per_type - type_counts.get(source_type, 0)
            selected_cases.extend(remaining[:needed])
    
    return selected_cases[:max_cases]


def create_analysis_template(case: Dict) -> str:
    """
    创建案例分析模板
    
    Args:
        case: 案例信息
    
    Returns:
        分析模板文本
    """
    template = f"""
# 案例深度分析

## 基本信息

- **案例标题**: {case['title']}
- **单位名称**: {case['unit_name']}
- **案例类型**: {case['source_type']}
- **日期**: {case['date']}
- **来源**: {case['website']}

## 案例内容

{case['full_content']}

---

## 深度分析

### 一、做法分析

**具体服务举措**：
[请分析该案例的具体服务举措和做法]

**服务模式**：
[请分析该案例采用的服务模式]

**创新要素**：
[请分析该案例的创新要素，如技术、机制、协同、文化等]

### 二、优势分析

**创新亮点**：
[请分析该案例的创新亮点和特色]

**实施效果**：
[请分析该案例的实施效果和价值]

**可推广性**：
[请分析该案例的可推广性和适用条件]

### 三、劣势分析

**局限性**：
[请分析该案例的局限性和不足之处]

**实施挑战**：
[请分析该案例实施过程中可能遇到的挑战和困难]

**适用条件**：
[请分析该案例的适用条件和前提]

### 四、武侯应用分析

#### 4.1 应用可能性

**适用性评估**：⭐⭐⭐⭐⭐ (1-5星)
[请评估该案例在武侯区供电中心应用的适用性]

**匹配度分析**：
[请分析该案例与武侯区实际情况的匹配度]

#### 4.2 可能遇到的问题

**问题1**：
[请分析可能遇到的第一个问题]

**问题2**：
[请分析可能遇到的第二个问题]

**问题3**：
[请分析可能遇到的第三个问题]

#### 4.3 实施方法建议

**方法建议**：
[请提供在武侯区实施该服务举措的具体方法建议]

**实施步骤**：
[请提供实施的具体步骤]

**资源配置**：
[请提供实施所需的资源配置建议]

#### 4.4 注意事项

**关键要点**：
[请列出实施过程中的关键要点]

**风险防控**：
[请列出风险防控措施]

**成功要素**：
[请列出确保成功的关键要素]

---

**分析完成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
    return template


def main():
    """主函数"""
    print("="*60)
    print("案例深度分析")
    print("="*60)
    
    # 读取案例数据库
    db_file = Path(__file__).parent / "cases-database" / "cases_database.json"
    with open(db_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    all_cases = data["cases"]
    print(f"\n总案例数: {len(all_cases)}")
    
    # 筛选典型案例
    selected_cases = select_typical_cases(all_cases, max_cases=35)
    print(f"筛选典型案例: {len(selected_cases)} 个")
    
    # 统计类型分布
    type_counts = {}
    for case in selected_cases:
        source_type = case["source_type"]
        type_counts[source_type] = type_counts.get(source_type, 0) + 1
    
    print("\n典型案例类型分布:")
    for source_type, count in type_counts.items():
        print(f"  {source_type}: {count} 个")
    
    # 保存筛选结果
    output_dir = Path(__file__).parent / "deep-analysis"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    selected_file = output_dir / "selected_cases.json"
    with open(selected_file, 'w', encoding='utf-8') as f:
        json.dump({
            "select_time": datetime.now().isoformat(),
            "total_count": len(selected_cases),
            "type_counts": type_counts,
            "cases": selected_cases
        }, f, ensure_ascii=False, indent=2)
    
    print(f"\n✓ 典型案例已保存: {selected_file}")
    
    # 生成分析模板列表
    templates_dir = output_dir / "templates"
    templates_dir.mkdir(parents=True, exist_ok=True)
    
    for i, case in enumerate(selected_cases, 1):
        template = create_analysis_template(case)
        template_file = templates_dir / f"case_{i:03d}_{case['source_type']}.md"
        with open(template_file, 'w', encoding='utf-8') as f:
            f.write(template)
    
    print(f"✓ 分析模板已生成: {templates_dir}")
    print(f"  共 {len(selected_cases)} 个模板文件")
    
    # 生成典型案例摘要
    summary_file = output_dir / "selected_cases_summary.md"
    with open(summary_file, 'w', encoding='utf-8') as f:
        f.write("# 典型案例筛选结果\n\n")
        f.write(f"**筛选时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write(f"**筛选数量**: {len(selected_cases)} 个典型案例\n\n")
        
        f.write("## 类型分布\n\n")
        for source_type, count in type_counts.items():
            f.write(f"- {source_type}: {count} 个\n")
        
        f.write("\n## 案例列表\n\n")
        
        for i, case in enumerate(selected_cases, 1):
            f.write(f"### {i}. {case['title']}\n\n")
            f.write(f"- **单位**: {case['unit_name']}\n")
            f.write(f"- **类型**: {case['source_type']}\n")
            f.write(f"- **评分**: {case['score']}\n")
            f.write(f"- **创新点**: {', '.join(case['innovation_keywords']) if case['innovation_keywords'] else '无'}\n")
            f.write(f"- **效果**: {', '.join(case['effect_keywords']) if case['effect_keywords'] else '无'}\n")
            f.write("\n")
    
    print(f"✓ 典型案例摘要已保存: {summary_file}")
    
    print(f"\n{'='*60}")
    print("案例筛选完成！")
    print(f"{'='*60}")
    print("\n下一步：")
    print("1. 使用AI辅助进行深度分析")
    print("2. 填充每个案例的分析模板")
    print("3. 形成深度分析报告")


if __name__ == "__main__":
    main()
