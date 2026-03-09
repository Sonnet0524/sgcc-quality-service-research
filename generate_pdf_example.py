#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
示例：使用md-to-pdf skill生成零成本优化方案的PDF文档
"""

import os
import sys

# 添加项目路径
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

from skills.md_to_pdf import generate_pdf

def main():
    """生成PDF文档"""
    
    # 定义输入输出文件
    md_file = "research/zero-cost-optimization-plan.md"
    output_file = "output/零成本工作模式优化方案.pdf"
    
    # 检查输入文件是否存在
    if not os.path.exists(md_file):
        print(f"❌ 输入文件不存在: {md_file}")
        return
    
    # 生成PDF
    try:
        print("🔄 正在生成PDF文档...")
        result = generate_pdf(
            md_file=md_file,
            output_file=output_file,
            title="武侯区供电中心优质服务提升方案",
            author="Research Agent"
        )
        
        file_size = os.path.getsize(result) / 1024
        print(f"\n✅ PDF生成成功！")
        print(f"📂 文件位置: {os.path.abspath(result)}")
        print(f"📊 文件大小: {file_size:.2f} KB")
        
    except ImportError as e:
        print(f"\n❌ 缺少依赖库: {str(e)}")
        print("\n请安装依赖:")
        print("  pip install markdown2 weasyprint")
        print("\n如果WeasyPrint安装困难，请参考 skills/md-to-pdf.md 中的故障排除部分")
        
    except Exception as e:
        print(f"\n❌ 生成失败: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
