#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
改进版Markdown转PDF生成器（使用reportlab）
专门用于生成零成本工作模式优化方案
支持完整的Markdown格式渲染
"""

import os
import re
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether
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
    
    # 主标题样式
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontName=font_name,
        fontSize=22,
        textColor=colors.HexColor('#1a5490'),
        alignment=TA_CENTER,
        spaceAfter=20,
        spaceBefore=20,
        borderWidth=0,
        borderPadding=0,
        borderColor=colors.HexColor('#1a5490'),
        borderRadius=None,
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
        leftIndent=0,
    )
    
    # 三级标题
    heading3_style = ParagraphStyle(
        'CustomHeading3',
        parent=styles['Heading3'],
        fontName=font_name,
        fontSize=14,
        textColor=colors.HexColor('#2e6da4'),
        spaceBefore=15,
        spaceAfter=10,
    )
    
    # 四级标题
    heading4_style = ParagraphStyle(
        'CustomHeading4',
        parent=styles['Heading4'],
        fontName=font_name,
        fontSize=12,
        textColor=colors.HexColor('#3d85c6'),
        spaceBefore=12,
        spaceAfter=8,
    )
    
    # 正文样式
    body_style = ParagraphStyle(
        'CustomBody',
        parent=styles['Normal'],
        fontName=font_name,
        fontSize=11,
        leading=18,
        alignment=TA_JUSTIFY,
        spaceBefore=4,
        spaceAfter=4,
    )
    
    # 列表样式
    bullet_style = ParagraphStyle(
        'CustomBullet',
        parent=styles['Normal'],
        fontName=font_name,
        fontSize=11,
        leading=16,
        leftIndent=15,
        spaceBefore=3,
        spaceAfter=3,
    )
    
    # 引用样式
    quote_style = ParagraphStyle(
        'CustomQuote',
        parent=styles['Normal'],
        fontName=font_name,
        fontSize=11,
        leading=16,
        leftIndent=20,
        textColor=colors.HexColor('#555555'),
        spaceBefore=8,
        spaceAfter=8,
        backColor=colors.HexColor('#f0f7ff'),
        borderPadding=10,
    )
    
    return {
        'title': title_style,
        'heading2': heading2_style,
        'heading3': heading3_style,
        'heading4': heading4_style,
        'body': body_style,
        'bullet': bullet_style,
        'quote': quote_style,
    }


def convert_markdown_formatting(text):
    """转换Markdown格式为reportlab支持的HTML格式"""
    # 处理粗体 **text** -> <b>text</b>
    text = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', text)
    
    # 处理斜体 *text* -> <i>text</i>
    text = re.sub(r'\*(.+?)\*', r'<i>\1</i>', text)
    
    # 处理行内代码 `code` -> <font name="Courier"><code></font>
    text = re.sub(r'`(.+?)`', r'<font name="Courier">\1</font>', text)
    
    # 处理删除线 ~~text~~ -> <strike>text</strike>
    text = re.sub(r'~~(.+?)~~', r'<strike>\1</strike>', text)
    
    # 处理特殊字符转义
    text = text.replace('&', '&amp;')
    text = text.replace('<b>', '###BOLD_START###')
    text = text.replace('</b>', '###BOLD_END###')
    text = text.replace('<i>', '###ITALIC_START###')
    text = text.replace('</i>', '###ITALIC_END###')
    text = text.replace('<font', '###FONT_START###')
    text = text.replace('</font>', '###FONT_END###')
    
    # 恢复HTML标签
    text = text.replace('###BOLD_START###', '<b>')
    text = text.replace('###BOLD_END###', '</b>')
    text = text.replace('###ITALIC_START###', '<i>')
    text = text.replace('###ITALIC_END###', '</i>')
    text = text.replace('###FONT_START###', '<font')
    text = text.replace('###FONT_END###', '</font>')
    
    return text


def parse_table(lines, start_index, styles):
    """解析表格"""
    table_lines = []
    i = start_index
    
    while i < len(lines) and '|' in lines[i]:
        if '---' not in lines[i]:  # 跳过分隔符行
            cells = [cell.strip() for cell in lines[i].split('|')[1:-1]]
            table_lines.append(cells)
        i += 1
    
    if not table_lines:
        return None, start_index
    
    # 创建表格
    table = Table(table_lines)
    
    # 设置表格样式
    table_style = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a5490')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, -1), 'Chinese'),
        ('FONTSIZE', (0, 0), (-1, 0), 11),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
        ('TOPPADDING', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 8),
        ('TOPPADDING', (0, 1), (-1, -1), 8),
        ('BACKGROUND', (0, 1), (-1, -1), colors.white),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f9f9f9')]),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#dddddd')),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ])
    
    table.setStyle(table_style)
    
    return table, i


def parse_markdown_section(line, styles):
    """解析Markdown行并返回对应的Flowable"""
    # 处理标题
    if line.startswith('# '):
        text = convert_markdown_formatting(line[2:])
        return Paragraph(text, styles['title'])
    elif line.startswith('## '):
        text = convert_markdown_formatting(line[3:])
        return Paragraph(text, styles['heading2'])
    elif line.startswith('### '):
        text = convert_markdown_formatting(line[4:])
        return Paragraph(text, styles['heading3'])
    elif line.startswith('#### '):
        text = convert_markdown_formatting(line[5:])
        return Paragraph(text, styles['heading4'])
    
    # 处理无序列表
    if line.startswith('- ') or line.startswith('* '):
        text = '• ' + convert_markdown_formatting(line[2:])
        return Paragraph(text, styles['bullet'])
    
    # 处理有序列表
    if re.match(r'^\d+\.\s', line):
        text = convert_markdown_formatting(line)
        return Paragraph(text, styles['bullet'])
    
    # 处理复选框列表
    if line.startswith('- [ ]') or line.startswith('- [x]'):
        checkbox = '☐' if '[ ]' in line else '☑'
        text = checkbox + ' ' + convert_markdown_formatting(line[6:])
        return Paragraph(text, styles['bullet'])
    
    # 处理引用
    if line.startswith('> '):
        text = convert_markdown_formatting(line[2:])
        return Paragraph(text, styles['quote'])
    
    # 处理分割线
    if line.startswith('---') or line.startswith('***'):
        return Spacer(1, 15)
    
    # 普通文本
    if line.strip():
        text = convert_markdown_formatting(line)
        return Paragraph(text, styles['body'])
    
    return Spacer(1, 8)


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
        bottomMargin=2.5*cm
    )
    
    # 创建样式
    styles = create_styles(font_name)
    
    # 读取Markdown文件
    with open(md_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # 解析内容
    story = []
    i = 0
    
    while i < len(lines):
        line = lines[i].rstrip()
        
        # 跳过文件开头的元数据（前15行）
        if i < 15:
            if '---' in line or line.startswith('description:') or \
               line.startswith('mode:') or line.startswith('version:'):
                i += 1
                continue
        
        # 检测表格
        if '|' in line and line.count('|') >= 2:
            table, next_i = parse_table(lines, i, styles)
            if table:
                story.append(table)
                story.append(Spacer(1, 10))
                i = next_i
                continue
        
        # 解析其他行
        flowable = parse_markdown_section(line, styles)
        if flowable:
            story.append(flowable)
        
        i += 1
    
    # 生成PDF
    doc.build(story)
    
    return output_file


def main():
    """主函数"""
    md_file = "research/zero-cost-optimization-plan.md"
    output_file = "output/零成本工作模式优化方案_改进版.pdf"
    
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
        print("\n改进内容：")
        print("- 粗体文本正确显示")
        print("- 斜体文本正确显示")
        print("- 表格格式优化")
        print("- 列表格式优化")
        print("- 引用格式美化")
        
    except Exception as e:
        print(f"\n生成失败: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
