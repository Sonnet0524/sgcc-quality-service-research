#!/bin/bash
# 使用pandoc将Markdown文档转换为Word文档

echo "=================================="
echo "Markdown转Word文档批量转换"
echo "=================================="
echo ""

# 进入output目录
cd output

# 定义转换函数
convert_md_to_docx() {
    local md_file=$1
    local docx_file="${md_file%.md}.docx"
    
    echo "转换: $md_file -> $docx_file"
    
    pandoc "$md_file" \
        -o "$docx_file" \
        --from markdown \
        --to docx \
        --reference-doc=/dev/null \
        --toc \
        --toc-depth=3 \
        --highlight-style=tango \
        --metadata title="$(basename "${md_file%.md}")"
    
    if [ $? -eq 0 ]; then
        echo "✓ 成功: $docx_file"
    else
        echo "✗ 失败: $md_file"
    fi
    echo ""
}

# 转换三个核心文档
echo "开始转换..."
echo ""

convert_md_to_docx "国网优质服务典型案例集.md"
convert_md_to_docx "服务模式分析框架.md"
convert_md_to_docx "武侯区供电中心服务提升应用建议.md"

echo "=================================="
echo "转换完成！"
echo "=================================="
echo ""
echo "生成的Word文档："
ls -lh *.docx 2>/dev/null || echo "无Word文档生成"

# 返回上级目录
cd ..
