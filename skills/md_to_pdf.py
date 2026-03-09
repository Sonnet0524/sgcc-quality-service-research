#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Markdown转PDF转换器

将Markdown文档转换为编排良好的PDF格式
支持中文排版、表格、列表等
"""

import os
import sys
import argparse
from typing import Optional, List, Dict

# 尝试导入必需的库
try:
    import markdown2
    from weasyprint import HTML, CSS
    HAS_WEASYPRINT = True
except ImportError:
    HAS_WEASYPRINT = False
    print("⚠️  警告: markdown2 或 weasyprint 未安装")
    print("请运行: pip install markdown2 weasyprint")


# 预设样式模板

DEFAULT_STYLE = """
@page {
    size: A4;
    margin: 2cm 2cm 2.5cm 2cm;
    @bottom-center {
        content: "第 " counter(page) " 页 / 共 " counter(pages) " 页";
        font-size: 10pt;
        color: #666;
    }
}

body {
    font-family: "Microsoft YaHei", "SimSun", "Arial", sans-serif;
    font-size: 11pt;
    line-height: 1.6;
    color: #333;
    text-align: justify;
}

h1 {
    font-size: 22pt;
    color: #1a5490;
    text-align: center;
    border-bottom: 3px solid #1a5490;
    padding-bottom: 10px;
    margin-top: 0;
    margin-bottom: 20px;
}

h2 {
    font-size: 16pt;
    color: #1a5490;
    border-left: 5px solid #1a5490;
    padding-left: 15px;
    margin-top: 25px;
    margin-bottom: 15px;
}

h3 {
    font-size: 13pt;
    color: #2e6da4;
    margin-top: 20px;
    margin-bottom: 12px;
}

h4 {
    font-size: 12pt;
    color: #3d85c6;
    margin-top: 15px;
    margin-bottom: 10px;
}

blockquote {
    background-color: #f0f7ff;
    border-left: 5px solid #1a5490;
    padding: 15px 20px;
    margin: 15px 0;
    font-style: italic;
    color: #555;
}

table {
    width: 100%;
    border-collapse: collapse;
    margin: 15px 0;
}

th {
    background-color: #1a5490;
    color: white;
    padding: 10px;
    text-align: left;
    font-weight: bold;
}

td {
    border: 1px solid #ddd;
    padding: 8px;
}

tr:nth-child(even) {
    background-color: #f9f9f9;
}

ul, ol {
    margin: 10px 0;
    padding-left: 25px;
}

li {
    margin: 5px 0;
}

strong {
    color: #1a5490;
    font-weight: bold;
}

hr {
    border: none;
    border-top: 2px solid #1a5490;
    margin: 20px 0;
}

p {
    margin: 8px 0;
    orphans: 3;
    widows: 3;
}

code {
    background-color: #f4f4f4;
    padding: 2px 6px;
    border-radius: 3px;
    font-family: "Courier New", monospace;
    font-size: 10pt;
}

tr {
    page-break-inside: avoid;
}

h2, h3, h4 {
    page-break-after: avoid;
}
"""

BUSINESS_STYLE = """
@page {
    size: A4;
    margin: 2.5cm;
    @bottom-center {
        content: counter(page);
        font-size: 10pt;
        color: #666;
    }
}

body {
    font-family: "Microsoft YaHei", "Arial", sans-serif;
    font-size: 11pt;
    line-height: 1.8;
    color: #333;
}

h1 {
    font-size: 20pt;
    color: #1976D2;
    text-align: center;
    border-bottom: 2px solid #1976D2;
    padding-bottom: 15px;
}

h2 {
    font-size: 15pt;
    color: #1976D2;
    border-left: 4px solid #1976D2;
    padding-left: 12px;
}

table {
    width: 100%;
    border-collapse: collapse;
    margin: 15px 0;
}

th {
    background-color: #1976D2;
    color: white;
    padding: 10px;
}

td {
    border: 1px solid #ddd;
    padding: 8px;
}
"""

ACADEMIC_STYLE = """
@page {
    size: A4;
    margin: 2.5cm;
}

body {
    font-family: "SimSun", "Times New Roman", serif;
    font-size: 12pt;
    line-height: 1.5;
    color: #000;
}

h1 {
    font-size: 18pt;
    text-align: center;
    font-weight: bold;
}

h2 {
    font-size: 14pt;
    font-weight: bold;
}

table {
    width: 100%;
    border-collapse: collapse;
    margin: 15px 0;
}

th, td {
    border: 1px solid #000;
    padding: 8px;
}
"""


class MarkdownToPDF:
    """Markdown转PDF转换器"""
    
    def __init__(self, css_style: str = DEFAULT_STYLE):
        """
        初始化转换器
        
        Args:
            css_style: CSS样式字符串
        """
        if not HAS_WEASYPRINT:
            raise RuntimeError("请先安装依赖库: pip install markdown2 weasyprint")
        
        self.css_style = css_style
    
    def convert(
        self,
        md_file: str,
        output_file: str,
        title: Optional[str] = None,
        author: Optional[str] = None
    ) -> str:
        """
        转换Markdown文件为PDF
        
        Args:
            md_file: Markdown文件路径
            output_file: 输出PDF文件路径
            title: 文档标题（可选）
            author: 作者信息（可选）
        
        Returns:
            输出文件路径
        """
        # 读取Markdown文件
        with open(md_file, "r", encoding="utf-8") as f:
            md_content = f.read()
        
        # 转换为HTML
        html_content = markdown2.markdown(
            md_content,
            extras=["tables", "fenced-code-blocks", "task_list", "header-ids"]
        )
        
        # 自定义CSS（添加页眉）
        css = self.css_style
        if title:
            css += f"""
@page {{
    @top-center {{
        content: "{title}";
        font-size: 10pt;
        color: #666;
    }}
}}
"""
        
        # 创建完整HTML
        full_html = f"""
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <title>{title or "Document"}</title>
</head>
<body>
    {html_content}
</body>
</html>
"""
        
        # 确保输出目录存在
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        
        # 生成PDF
        HTML(string=full_html).write_pdf(
            output_file,
            stylesheets=[CSS(string=css)]
        )
        
        return output_file


def generate_pdf(
    md_file: str,
    output_file: str,
    title: Optional[str] = None,
    author: Optional[str] = None,
    css_style: str = DEFAULT_STYLE
) -> str:
    """
    快捷函数：生成PDF文档
    
    Args:
        md_file: Markdown文件路径
        output_file: 输出PDF文件路径
        title: 文档标题（可选）
        author: 作者信息（可选）
        css_style: CSS样式（可选）
    
    Returns:
        输出文件路径
    """
    converter = MarkdownToPDF(css_style=css_style)
    return converter.convert(md_file, output_file, title, author)


def batch_convert(
    input_dir: str,
    output_dir: str,
    pattern: str = "*.md"
) -> List[str]:
    """
    批量转换目录下的Markdown文件
    
    Args:
        input_dir: 输入目录
        output_dir: 输出目录
        pattern: 文件匹配模式
    
    Returns:
        生成的PDF文件列表
    """
    import glob
    
    md_files = glob.glob(os.path.join(input_dir, pattern))
    pdf_files = []
    
    converter = MarkdownToPDF()
    
    for md_file in md_files:
        base_name = os.path.splitext(os.path.basename(md_file))[0]
        output_file = os.path.join(output_dir, f"{base_name}.pdf")
        
        try:
            converter.convert(md_file, output_file)
            pdf_files.append(output_file)
            print(f"✅ 已转换: {md_file} -> {output_file}")
        except Exception as e:
            print(f"❌ 转换失败 {md_file}: {str(e)}")
    
    return pdf_files


def main():
    """命令行入口"""
    parser = argparse.ArgumentParser(description="Markdown转PDF转换器")
    parser.add_argument("--input", "-i", required=True, help="输入Markdown文件")
    parser.add_argument("--output", "-o", required=True, help="输出PDF文件")
    parser.add_argument("--title", "-t", help="文档标题")
    parser.add_argument("--style", "-s", 
                       choices=["default", "business", "academic"],
                       default="default",
                       help="样式模板")
    
    args = parser.parse_args()
    
    # 选择样式
    styles = {
        "default": DEFAULT_STYLE,
        "business": BUSINESS_STYLE,
        "academic": ACADEMIC_STYLE
    }
    
    try:
        output = generate_pdf(
            md_file=args.input,
            output_file=args.output,
            title=args.title,
            css_style=styles[args.style]
        )
        print(f"✅ PDF生成成功: {output}")
        print(f"📄 文件大小: {os.path.getsize(output) / 1024:.2f} KB")
    except Exception as e:
        print(f"❌ 生成失败: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
