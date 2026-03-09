#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简化版Markdown转PDF生成器（使用reportlab）
专门用于生成零成本工作模式优化方案
"""

import os
import re
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY


def register_chinese_fonts():
    """注册中文字体"""
    # 尝试注册常见的中文字体
    font_paths = [
        "C:/Windows/Fonts/msyh.ttc",  # 微软雅黑
        "C:/Windows/Fonts/simsun.ttc",  # 宋体
        "C:/Windows/Fonts/simhei.ttf",  # 黑体
    ]
    
    font_name = "Chinese"
    for font_path in font_paths:
        if os.path.exists(font_path):
            try:
                pdfmetrics.registerFont(TTFont(font_name, font_path))
                return font_name
            except:
                continue
    
    # 如果都找不到，返回默认字体
    return "Helvetica"


def create_styles(font_name):
    """创建文档样式"""
    styles = getSampleStyleSheet()
    
    # 标题样式
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontName=font_name,
        fontSize=20,
        textColor=colors.HexColor('#1a5490'),
        alignment=TA_CENTER,
        spaceAfter=30,
        spaceBefore=20,
    )
    
    # 二级标题
    heading2_style = ParagraphStyle(
        'CustomHeading2',
        parent=styles['Heading2'],
        fontName=font_name,
        fontSize=16,
        textColor=colors.HexColor('#1a5490'),
        spaceBefore=20,
        spaceAfter=12,
    )
    
    # 三级标题
    heading3_style = ParagraphStyle(
        'CustomHeading3',
        parent=styles['Heading3'],
        fontName=font_name,
        fontSize=13,
        textColor=colors.HexColor('#2e6da4'),
        spaceBefore=15,
        spaceAfter=10,
    )
    
    # 正文样式
    body_style = ParagraphStyle(
        'CustomBody',
        parent=styles['Normal'],
        fontName=font_name,
        fontSize=11,
        leading=18,
        alignment=TA_JUSTIFY,
        spaceBefore=6,
        spaceAfter=6,
    )
    
    # 列表样式
    bullet_style = ParagraphStyle(
        'CustomBullet',
        parent=styles['Normal'],
        fontName=font_name,
        fontSize=11,
        leading=16,
        leftIndent=20,
        spaceBefore=3,
        spaceAfter=3,
    )
    
    return {
        'title': title_style,
        'heading2': heading2_style,
        'heading3': heading3_style,
        'body': body_style,
        'bullet': bullet_style,
    }


def parse_markdown_section(line, styles):
    """解析Markdown行并返回对应的Flowable"""
    # 处理标题
    if line.startswith('# '):
        return Paragraph(line[2:], styles['title'])
    elif line.startswith('## '):
        return Paragraph(line[3:], styles['heading2'])
    elif line.startswith('### '):
        return Paragraph(line[4:], styles['heading3'])
    elif line.startswith('#### '):
        return Paragraph(line[5:], styles['heading3'])
    
    # 处理列表
    if line.startswith('- ') or line.startswith('* '):
        text = '• ' + line[2:]
        return Paragraph(text, styles['bullet'])
    if re.match(r'^\d+\.', line):
        return Paragraph(line, styles['bullet'])
    
    # 处理引用
    if line.startswith('> '):
        text = '<i>' + line[2:] + '</i>'
        return Paragraph(text, styles['body'])
    
    # 处理分割线
    if line.startswith('---'):
        return Spacer(1, 10)
    
    # 普通文本
    if line.strip():
        # 处理粗体
        text = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', line)
        return Paragraph(text, styles['body'])
    
    return Spacer(1, 6)


def create_pdf(md_file, output_file, title="文档"):
    """生成PDF文档"""
    
    # 注册中文字体
    font_name = register_chinese_fonts()
    
    # 创建PDF文档
    doc = SimpleDocTemplate(
        output_file,
        pagesize=A4,
        rightMargin=2*cm,
        leftMargin=2*cm,
        topMargin=2*cm,
        bottomMargin=2*cm
    )
    
    # 创建样式
    styles = create_styles(font_name)
    
    # 读取Markdown文件
    with open(md_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # 解析内容
    story = []
    skip_header = False
    
    for i, line in enumerate(lines):
        line = line.rstrip()
        
        # 跳过文件开头的元数据
        if i < 15 and ('---' in line or line.startswith('description:') or 
                       line.startswith('mode:') or line.startswith('version:') or
                       line.startswith('>') or line.startswith('**')):
            skip_header = True
            continue
        
        # 检测表格
        if '|' in line and line.count('|') >= 2:
            # 简化处理：跳过表格行和分隔符行
            if '---' not in line:
                # 将表格内容转为普通文本
                cells = [cell.strip() for cell in line.split('|')[1:-1]]
                text = '  |  '.join(cells)
                story.append(Paragraph(text, styles['body']))
            continue
        
        # 解析其他行
        flowable = parse_markdown_section(line, styles)
        if flowable:
            story.append(flowable)
    
    # 生成PDF
    doc.build(story)
    
    return output_file


def main():
    """主函数"""
    md_file = "research/zero-cost-optimization-plan.md"
    output_file = "output/零成本工作模式优化方案.pdf"
    
    # 确保输出目录存在
    os.makedirs("output", exist_ok=True)
    
    try:
        print("正在生成PDF文档...")
        result = create_pdf(
            md_file=md_file,
            output_file=output_file,
            title="武侯区供电中心优质服务提升方案"
        )
        
        file_size = os.path.getsize(result) / 1024
        print(f"\nPDF生成成功！")
        print(f"文件位置: {os.path.abspath(result)}")
        print(f"文件大小: {file_size:.2f} KB")
        
    except Exception as e:
        print(f"\n生成失败: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
