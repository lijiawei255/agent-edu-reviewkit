---
name: output-generation
description: 复习文档的双格式输出规则——HTML生成、PDF生成、中文编码与字体处理。被 course-review-guide 引用。确保HTML在浏览器中正确渲染、PDF不出现中文乱码或排版错误。
---

# 双格式输出规则：HTML + PDF

## 核心要求

> **每次生成复习文档时，必须同时产出 HTML 和 PDF 两种格式，两者均须通过质量检查。**

## 1. HTML 输出规范

### 1.1 字符编码

- 文件必须以 UTF-8 编码保存
- `<meta charset="UTF-8">` 必须是 `<head>` 的第一个子元素
- 所有 Python 写入脚本必须在文件操作中指定 `encoding='utf-8'`

### 1.2 中文字体栈

CSS `--font-body` 变量必须包含完整的中文后备字体链：

```css
--font-body: system-ui, -apple-system, "Segoe UI", "Noto Sans SC",
             "PingFang SC", "Microsoft YaHei", "WenQuanYi Micro Hei",
             sans-serif;
--font-mono: "JetBrains Mono", "Fira Code", "Cascadia Code",
            "Noto Sans Mono CJK SC", "Consolas", monospace;
```

### 1.3 MathJax 配置

使用 MathJax 3，local-first + CDN fallback：

```html
<script>
window.MathJax = {
  tex: {
    inlineMath: [['$', '$'], ['\\(', '\\)']],
    displayMath: [['$$', '$$'], ['\\[', '\\]']],
    tags: 'ams'
  },
  svg: { fontCache: 'global' },
  options: {
    enableMenu: false,  // 禁止公式右键菜单，防止转PDF时出问题
    skipHtmlTags: ['script', 'noscript', 'style', 'textarea', 'pre']
  }
};
</script>
<script id="MathJax-script" async src="./mathjax/es5/tex-svg.js"
  onerror="var cdn=document.createElement('script');
           cdn.src='https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-svg.js';
           this.remove();document.head.appendChild(cdn);">
</script>
```

### 1.4 图片处理

- HTML生成时先使用相对路径引用图片
- HTML完成后运行 `python embed_images.py <文件名>.html --in-place` 将图片转为base64
- 内嵌后的HTML是完全自包含的，不依赖外部图片文件

## 2. PDF 输出规范（🔴 核心新增）

### 2.1 PDF生成方式

使用 **weasyprint** 从HTML生成PDF（保留MathJax渲染的SVG公式和CSS样式）：

```bash
pip install weasyprint
python -m weasyprint input.html output.pdf
```

### 2.2 PDF专用CSS（🔴 防止中文乱码）

在HTML的 `<style>` 中必须包含以下PDF专用样式：

```css
@media print {
  /* PDF中文不乱码的核心：指定系统安装的中文字体 */
  body {
    font-family: "Noto Sans SC", "PingFang SC", "Microsoft YaHei",
                 "SimSun", "Songti SC", serif !important;
    font-size: 11pt;
    line-height: 1.7;
    color: #000;
    background: #fff;
  }

  /* 代码块字体 */
  pre, code {
    font-family: "Noto Sans Mono CJK SC", "Consolas", "Courier New", monospace !important;
    font-size: 9pt;
  }

  /* 确保MathJax SVG公式在PDF中可见 */
  mjx-container {
    display: inline-block !important;
  }
  mjx-container[display="true"] {
    display: block !important;
    margin: 0.8em 0;
  }

  /* 分页控制 */
  .chapter-card {
    page-break-before: always;
    page-break-inside: avoid;
  }
  h2, h3 {
    page-break-after: avoid;
  }
  .callout, details, figure, table {
    page-break-inside: avoid;
  }
  img, svg {
    max-width: 100%;
    page-break-inside: avoid;
  }

  /* 交互元素在PDF中静默隐藏或展开 */
  .search-container, .toc-sidebar, .progress-tracker,
  .tab-buttons, .flashcard {
    display: none !important;
  }
  .toc-inline {
    display: block;
    border: 1px solid #ccc;
  }
  /* 展开所有折叠内容 */
  details.derive-steps, details.quiz-answer {
    display: block !important;
  }
  details.derive-steps > summary::before {
    display: none;
  }
  details.derive-steps > .derive-content {
    display: block;
  }
  .tab-panel {
    display: block !important;
  }

  /* 链接去掉颜色 */
  a {
    color: #000;
    text-decoration: underline;
  }

  /* 封面在PDF中简化 */
  .hero {
    background: #fff !important;
    color: #000;
    border-bottom: 3px solid #000;
    padding: 1.5rem 0;
  }
  .hero h1 { color: #000; }
  .hero .meta-card {
    background: #f5f5f5;
    border: 1px solid #ccc;
    color: #000;
  }
}
```

### 2.3 PDF字体配置（weasyprint）

创建字体配置文件或在生成命令中指定：

```python
# pdf_config.py —— PDF生成前的字体检查与配置
import subprocess
import sys

def check_fonts():
    """检查系统是否有中文字体"""
    required = ['Noto Sans SC', 'Microsoft YaHei', 'SimSun', 'PingFang SC']
    # Windows: 检查 C:\Windows\Fonts\
    # macOS: 检查 /System/Library/Fonts/ 和 ~/Library/Fonts/
    # Linux: 检查 fc-list 输出
    ...

def generate_pdf(html_path, pdf_path):
    """生成PDF，确保字体正确"""
    cmd = [
        sys.executable, '-m', 'weasyprint',
        '--encoding', 'utf-8',
        '--presentational-hints',
        html_path, pdf_path
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"PDF生成失败: {result.stderr}")
        # 降级方案：提示用户安装中文字体或使用浏览器打印
    return result.returncode == 0
```

### 2.4 PDF无法自动生成时的降级方案

如果 `weasyprint` 不可用或中文字体缺失，向用户提供以下手动方案：

```
⚠ PDF自动生成失败。请通过以下方式手动导出PDF：
1. 在浏览器（Chrome/Edge）中打开生成的HTML文件
2. 按 Ctrl+P 打开打印对话框
3. 目标打印机选择"另存为PDF"
4. 在"更多设置"中确保：
   - 边距：默认
   - 勾选"背景图形"
   - 纸张大小：A4
5. 点击保存
```

## 3. 生成流程

### 3.1 完整生成命令序列

```bash
# Step 1: 生成HTML（通过Python追加脚本）
python _append_ch0_1.py
python _append_ch3_4.py
...

# Step 2: 内嵌图片
python embed_images.py review.html --in-place

# Step 3: 生成PDF
python -m weasyprint review.html review.pdf
# 或使用自定义脚本
python generate_pdf.py review.html review.pdf

# Step 4: 清理临时文件
rm _append_*.py
```

### 3.2 质量检查清单（双格式）

HTML 和 PDF 各需通过以下检查：

**HTML检查**：
- [ ] 在Chrome/Edge/Firefox中打开，页面正常渲染
- [ ] 所有MathJax公式正确显示（无原始LaTeX代码裸露）
- [ ] 搜索功能正常
- [ ] 闪卡点击翻转正常
- [ ] 选项卡切换正常
- [ ] 进度追踪checkbox正常工作
- [ ] 移动端响应式布局正常

**PDF检查**：
- [ ] 中文字符正常显示（无乱码、无方块、无?替代）
- [ ] 数学公式正常渲染（包括上下标、分式、根号、矩阵）
- [ ] 图片可见且位置正确
- [ ] 页码、页眉页脚完整
- [ ] 代码块不超出页面边界
- [ ] 表格不被截断
- [ ] 链接可点击（如果是交互式PDF）

## 4. 编码与兼容性注意事项

### 4.1 Windows GBK陷阱

Windows环境下Python默认使用GBK编码，容易导致中文乱码：

```python
# 所有文件操作必须显式指定UTF-8
with open('file.html', 'w', encoding='utf-8') as f:
    f.write(content)

# Python脚本本身也必须保存为UTF-8
# 脚本文件头添加: # -*- coding: utf-8 -*-
```

### 4.2 特殊字符处理

- HTML实体：`&amp;` `&lt;` `&gt;` `&quot;`
- LaTeX中的特殊字符必须正确转义
- 中文引号 `""` 和英文引号 `""` 必须区分
