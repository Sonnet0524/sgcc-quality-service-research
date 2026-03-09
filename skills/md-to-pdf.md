# Skill: Markdown转PDF文档生成器

## 📋 Skill描述

**名称**: md-to-pdf  
**版本**: 1.0  
**用途**: 将Markdown文档转换为编排良好的PDF格式  
**适用场景**: 生成报告、方案文档、技术文档等

---

## 🎯 功能特点

- ✅ **高质量排版**: 支持中文，专业排版样式
- ✅ **自动分页**: 智能处理分页，避免孤行寡行
- ✅ **表格支持**: 完美支持Markdown表格
- ✅ **页眉页脚**: 自动添加页眉页脚和页码
- ✅ **代码高亮**: 支持代码块显示
- ✅ **自定义样式**: 可自定义CSS样式

---

## 📦 依赖安装

### 必需的Python库

```bash
pip install markdown2 weasyprint Pillow
```

### Windows系统额外依赖

WeasyPrint在Windows上需要GTK+库支持。如果遇到问题，可以：

**方案1：使用预编译包**
```bash
pip install weasyprint
```

**方案2：使用替代方案（推荐）**
如果WeasyPrint安装困难，可以使用reportlab或fpdf2：
```bash
pip install markdown2 reportlab fpdf2
```

---

## 🚀 使用方法

### 方法1：使用预设脚本

```python
from skills.md_to_pdf import generate_pdf

# 生成PDF
output_file = generate_pdf(
    md_file="path/to/document.md",
    output_file="output/document.pdf",
    title="文档标题"
)
```

### 方法2：使用命令行

```bash
python skills/md_to_pdf.py --input research/document.md --output output/document.pdf
```

### 方法3：集成到工作流

```python
import sys
sys.path.insert(0, 'D:\\opencode\\github\\sgcc-quality-service-research')

from skills.md_to_pdf import MarkdownToPDF

# 创建转换器
converter = MarkdownToPDF()

# 转换文档
converter.convert(
    md_file="research/zero-cost-optimization-plan.md",
    output_file="output/优化方案.pdf"
)
```

---

## 📝 示例代码

### 基础示例

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Markdown转PDF示例
"""

import os
import sys

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from skills.md_to_pdf import generate_pdf

def main():
    # 定义输入输出文件
    md_file = "research/zero-cost-optimization-plan.md"
    output_file = "output/零成本工作模式优化方案.pdf"
    
    # 生成PDF
    try:
        result = generate_pdf(
            md_file=md_file,
            output_file=output_file,
            title="武侯区供电中心优质服务提升方案",
            author="Research Agent"
        )
        print(f"✅ PDF生成成功: {result}")
    except Exception as e:
        print(f"❌ 生成失败: {str(e)}")

if __name__ == "__main__":
    main()
```

### 自定义样式示例

```python
from skills.md_to_pdf import MarkdownToPDF

# 自定义CSS样式
custom_css = """
@page {
    size: A4;
    margin: 2cm;
    @bottom-center {
        content: "第 " counter(page) " 页";
    }
}

body {
    font-family: "SimSun", serif;
    font-size: 12pt;
}

h1 {
    color: #D32F2F;
    text-align: center;
}
"""

# 创建转换器并应用自定义样式
converter = MarkdownToPDF(css_style=custom_css)
converter.convert("document.md", "output.pdf")
```

---

## 🔧 高级功能

### 1. 批量转换

```python
from skills.md_to_pdf import batch_convert

# 批量转换目录下所有Markdown文件
batch_convert(
    input_dir="research/",
    output_dir="output/",
    pattern="*.md"
)
```

### 2. 添加封面

```python
from skills.md_to_pdf import generate_pdf_with_cover

generate_pdf_with_cover(
    md_file="document.md",
    output_file="output.pdf",
    cover_info={
        "title": "优质服务提升方案",
        "subtitle": "零成本工作模式优化版",
        "author": "Research Agent",
        "date": "2026-03-09",
        "organization": "武侯区供电中心"
    }
)
```

### 3. 合并多个文档

```python
from skills.md_to_pdf import merge_and_convert

# 合并多个Markdown文件为一个PDF
merge_and_convert(
    md_files=["part1.md", "part2.md", "part3.md"],
    output_file="complete.pdf",
    add_page_break=True
)
```

---

## 📊 样式定制

### 预设样式模板

**1. 商务报告样式**
```python
from skills.md_to_pdf import BUSINESS_STYLE

converter = MarkdownToPDF(css_style=BUSINESS_STYLE)
```

**2. 学术论文样式**
```python
from skills.md_to_pdf import ACADEMIC_STYLE

converter = MarkdownToPDF(css_style=ACADEMIC_STYLE)
```

**3. 技术文档样式**
```python
from skills.md_to_pdf import TECHNICAL_STYLE

converter = MarkdownToPDF(css_style=TECHNICAL_STYLE)
```

### 自定义CSS

```python
custom_css = """
/* 页面设置 */
@page {
    size: A4;
    margin: 2cm;
}

/* 正文样式 */
body {
    font-family: "Microsoft YaHei", sans-serif;
    font-size: 11pt;
    line-height: 1.8;
    color: #333;
}

/* 标题样式 */
h1 { font-size: 20pt; color: #1976D2; }
h2 { font-size: 16pt; color: #1976D2; }
h3 { font-size: 14pt; color: #2196F3; }

/* 表格样式 */
table {
    width: 100%;
    border-collapse: collapse;
}

th {
    background-color: #1976D2;
    color: white;
}

td {
    border: 1px solid #ddd;
}
"""

converter = MarkdownToPDF(css_style=custom_css)
```

---

## ⚙️ 配置选项

### 可配置参数

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| md_file | str | 必需 | 输入的Markdown文件路径 |
| output_file | str | 必需 | 输出的PDF文件路径 |
| title | str | None | 文档标题（显示在页眉） |
| author | str | None | 作者信息 |
| css_style | str | DEFAULT_STYLE | CSS样式 |
| page_size | str | "A4" | 页面大小（A4/Letter等） |
| margin | str | "2cm" | 页边距 |
| encoding | str | "utf-8" | 文件编码 |

---

## 🔍 故障排除

### 常见问题

**问题1：WeasyPrint安装失败**

**解决方案**：
```bash
# Windows用户可以使用conda
conda install -c conda-forge weasyprint

# 或者使用替代方案
pip install markdown2 reportlab
```

**问题2：中文字体显示异常**

**解决方案**：
```python
# 在CSS中指定中文字体
css = """
body {
    font-family: "Microsoft YaHei", "SimSun", "SimHei", sans-serif;
}
"""
```

**问题3：表格跨页断裂**

**解决方案**：
```css
table {
    page-break-inside: avoid;
}

tr {
    page-break-inside: avoid;
}
```

**问题4：图片无法显示**

**解决方案**：
- 确保图片路径正确
- 使用绝对路径或将图片放在同一目录
- 支持的格式：PNG, JPG, SVG

---

## 📚 技术原理

### 转换流程

```
Markdown文件
    ↓
markdown2解析
    ↓
HTML文档
    ↓
CSS样式应用
    ↓
WeasyPrint渲染
    ↓
PDF文档
```

### 核心技术

- **markdown2**: 将Markdown转换为HTML
- **WeasyPrint**: 将HTML+CSS渲染为PDF
- **CSS Paged Media**: 控制PDF页面布局和样式

---

## 💡 最佳实践

### 1. Markdown编写建议

```markdown
# 一级标题（文档标题）

> 重要提示或引言

## 二级标题（章节）

### 三级标题（小节）

#### 四级标题（要点）

**重点内容用粗体**

- 列表项使用短句
- 避免过长的段落

| 表格 | 建议 |
|------|------|
| 简洁 | 明了 |
```

### 2. 性能优化

- 对于大型文档，先分割成多个小文档
- 使用 `page-break-inside: avoid` 防止内容断裂
- 压缩图片以减小PDF文件大小

### 3. 质量保证

- 生成后检查分页是否合理
- 确认表格没有跨页断裂
- 验证中文显示是否正常

---

## 📖 参考资源

### 官方文档

- [markdown2文档](https://github.com/trentm/python-markdown2)
- [WeasyPrint文档](https://weasyprint.org/)
- [CSS Paged Media](https://www.w3.org/TR/css-page-3/)

### 相关技能

- `literature-review`: 文献检索和分析
- `observation`: 系统化观察和记录
- `theory-building`: 理论框架构建

---

## 🔄 更新日志

### v1.0 (2026-03-09)
- ✅ 初始版本发布
- ✅ 支持基础Markdown转PDF
- ✅ 支持中文排版
- ✅ 支持表格和列表
- ✅ 支持自定义样式

### 计划功能
- [ ] 封面生成功能
- [ ] 目录自动生成
- [ ] 批量转换功能
- [ ] 在线预览功能

---

## 📞 技术支持

如遇问题，请检查：
1. Python版本（建议3.8+）
2. 依赖库是否正确安装
3. Markdown语法是否正确
4. 文件路径是否正确

---

**维护者**: Research Agent  
**创建时间**: 2026-03-09  
**最后更新**: 2026-03-09  
**Skill类型**: 文档处理
