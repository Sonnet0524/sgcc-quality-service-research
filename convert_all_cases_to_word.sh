#!/bin/bash
# 批量转换所有案例Markdown文件为Word文档

echo "=================================="
echo "批量转换案例文件为Word文档"
echo "=================================="
echo ""

# 定义源目录和目标目录
SOURCE_DIR="deep-analysis/analyzed"
TARGET_DIR="deep-analysis/analyzed-word"

# 创建目标目录
mkdir -p "$TARGET_DIR"

# 计数器
total=0
success=0
failed=0

echo "开始转换..."
echo ""

# 遍历所有MD文件
for md_file in "$SOURCE_DIR"/*.md; do
    if [ -f "$md_file" ]; then
        # 获取文件名（不含路径）
        filename=$(basename "$md_file")
        # 转换为docx文件名
        docx_file="$TARGET_DIR/${filename%.md}.docx"
        
        echo "[$((total+1))] 转换: $filename"
        
        # 使用pandoc转换
        pandoc "$md_file" -o "$docx_file" --from markdown --to docx
        
        if [ $? -eq 0 ]; then
            echo "    ✓ 成功"
            ((success++))
        else
            echo "    ✗ 失败"
            ((failed++))
        fi
        
        ((total++))
    fi
done

echo ""
echo "=================================="
echo "转换完成！"
echo "=================================="
echo ""
echo "统计信息："
echo "  总文件数: $total"
echo "  成功转换: $success"
echo "  失败数量: $failed"
echo ""
echo "生成的Word文档保存在: $TARGET_DIR/"
echo ""
ls -lh "$TARGET_DIR"/*.docx | head -10
echo "..."
echo "共生成 $(ls "$TARGET_DIR"/*.docx | wc -l | tr -d ' ') 个Word文档"
