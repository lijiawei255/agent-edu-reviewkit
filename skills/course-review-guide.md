---
name: course-review-guide
description: 将课程原始课件（PDF/PPTX/DOCX）转化为图文并茂的高质量HTML考试复习文档。当用户提到"整理复习文档"、"生成复习指南"、"课件转复习资料"、"考试复习"、"期末/期中复习"、"整理课程笔记"时触发此技能。适用于任何课程的复习文档生成。
---

# 课程复习文档生成器（HTML版）

## 概述

本技能将课程原始课件一键转化为高质量、结构化、图文并茂的**单文件HTML考试复习文档**。输出包含MathJax数学排版、内联SVG示意图、课件原图、完整公式推导、例题详解、答题模板和常见错误附录。**公式残缺处自动还原，推导跳跃处自动补全，确保基础薄弱的学生仅靠本文档即可高效复习。**

---

## Phase 1：信息收集与范围确认

### 1.1 确认课件位置

向用户询问课件文件所在的目录路径。如果用户未提供，请用户将所有课件文件放入一个目录。

### 1.2 扫描课件文件

使用 Glob 或 Bash（`ls`）扫描课件目录，列出所有 `.pdf`、`.pptx`、`.docx` 文件及其变体（`.pptm`、`.dotx`、`.dotm`），以表格呈现文件名和大小。

### 1.3 确认考试范围

逐项确认以下信息：

1. **考试范围**：哪些章节/讲座在考试范围内？哪些明确不考？
2. **课程全称**：中文全称和英文全称
3. **授课教师**：姓名和单位（如有）
4. **参考教材**：书名、作者、版本（如有）
5. **考试形式**：闭卷/开卷/半开卷
6. **授课语言**：中文/英文/双语
7. **输出文件名**：期望的 `.html` 输出文件名

### 1.4 创建输出目录

在课件目录下创建 `extracted_text/` 和 `extracted_images/`。

---

## Phase 2：课件内容提取

### 2.1 提供提取脚本

让用户将以下脚本保存为 `extract_course_materials.py` 并放在课件目录下，修改配置区路径后运行。

```python
"""
课程课件内容提取工具 —— 文本 + 图片
支持格式: .pdf (pypdf), .pptx/.pptm (python-pptx), .docx/.dotx/.dotm (python-docx + zipfile)
所有依赖均为纯Python库，pip一键安装，无C编译依赖。

使用方法:
  1. 修改下方"配置区"的 课件目录、文本输出目录、图片输出目录
  2. 运行: python extract_course_materials.py
"""

import os
import sys
import zipfile
from pathlib import Path

# 修复Windows控制台编码问题（GBK无法输出Unicode字符如 ✓ ✗）
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

# ============================================================
# 0. 依赖自检
# ============================================================
MISSING = []
try:
    from pypdf import PdfReader
except ImportError:
    MISSING.append("pypdf")
try:
    from pptx import Presentation
    from pptx.enum.shapes import MSO_SHAPE_TYPE
except ImportError:
    MISSING.append("python-pptx")
try:
    from docx import Document
except ImportError:
    MISSING.append("python-docx")

if MISSING:
    print("=" * 50)
    print("以下 Python 库未安装，请先运行：")
    print(f"  pip install {' '.join(MISSING)}")
    print("=" * 50)
    sys.exit(1)

# ============================================================
# 1. 配置区 —— 用户根据需要修改以下变量
# ============================================================
课件目录 = r"课件"
文本输出目录 = r"extracted_text"
图片输出目录 = r"extracted_images"

os.makedirs(文本输出目录, exist_ok=True)
os.makedirs(图片输出目录, exist_ok=True)

# ============================================================
# 2. 工具函数
# ============================================================

def _content_type_to_ext(content_type):
    mapping = {
        "image/png": ".png", "image/jpeg": ".jpg", "image/gif": ".gif",
        "image/bmp": ".bmp", "image/tiff": ".tiff", "image/webp": ".webp",
        "image/x-png": ".png", "image/x-emf": ".emf", "image/x-wmf": ".wmf",
    }
    return mapping.get(content_type, ".png")

def _guess_ext_from_bytes(data):
    if data[:4] == b'\x89PNG': return '.png'
    if data[:2] == b'\xff\xd8': return '.jpg'
    if data[:4] == b'GIF8': return '.gif'
    if data[:2] == b'BM': return '.bmp'
    if data[:4] == b'RIFF' and data[8:12] == b'WEBP': return '.webp'
    return '.png'

def _sanitize_filename(s):
    illegal = '<>:"/\\|?*'
    for c in illegal:
        s = s.replace(c, '_')
    return s

# ============================================================
# 3. 纯图片文件预检
# ============================================================

def _check_likely_image_only(filepath, ext):
    """预检文件是否可能是纯图片型（扫描版PDF等）"""
    if ext == '.pdf':
        try:
            from pypdf import PdfReader
            reader = PdfReader(filepath)
            if len(reader.pages) == 0:
                return False
            # 检查前三页的文本量
            total_chars = 0
            for page in reader.pages[:3]:
                text = page.extract_text()
                if text:
                    total_chars += len(text.strip())
            # 前三页均无有效文本 → 大概率是扫描版
            return total_chars < 50
        except Exception:
            return False
    return False

# ============================================================
# 4. 格式提取函数
# ============================================================

def extract_pdf(filepath, basename):
    reader = PdfReader(filepath)
    lines = []
    img_count = 0

    for i, page in enumerate(reader.pages):
        page_num = i + 1
        text = page.extract_text()
        if text and text.strip():
            lines.append(f"\n--- 第{page_num}页 ---")
            lines.append(text)
        try:
            for j, img_obj in enumerate(page.images):
                img_data = img_obj.data
                if not img_data or len(img_data) < 100:
                    continue
                ext = _guess_ext_from_bytes(img_data)
                img_name = f"{basename}_p{page_num}_img{j+1}{ext}"
                img_path = os.path.join(图片输出目录, img_name)
                with open(img_path, "wb") as f:
                    f.write(img_data)
                lines.append(f"[图片: {img_name}]")
                img_count += 1
        except Exception:
            pass

    return "\n".join(lines), len(reader.pages), img_count

def extract_pptx(filepath, basename):
    prs = Presentation(filepath)
    lines = []
    img_count = 0

    for i, slide in enumerate(prs.slides):
        slide_num = i + 1
        slide_texts = []
        for shape in slide.shapes:
            if shape.shape_type == MSO_SHAPE_TYPE.PICTURE:
                try:
                    img_blob = shape.image.blob
                    if img_blob and len(img_blob) >= 100:
                        ext = _content_type_to_ext(shape.image.content_type)
                        img_name = f"{basename}_s{slide_num}_img{img_count+1}{ext}"
                        img_path = os.path.join(图片输出目录, img_name)
                        with open(img_path, "wb") as f:
                            f.write(img_blob)
                        slide_texts.append(f"[图片: {img_name}]")
                        img_count += 1
                except Exception:
                    pass
            if shape.has_text_frame:
                for para in shape.text_frame.paragraphs:
                    t = para.text.strip()
                    if t:
                        slide_texts.append(t)
            if shape.has_table:
                table = shape.table
                for row in table.rows:
                    row_texts = []
                    for cell in row.cells:
                        ct = cell.text.strip().replace("\n", " ")
                        row_texts.append(ct)
                    slide_texts.append(" | ".join(row_texts))
        if slide_texts:
            lines.append(f"\n--- 第{slide_num}张幻灯片 ---")
            lines.append("\n".join(slide_texts))

    return "\n".join(lines), len(prs.slides), img_count

def extract_docx(filepath, basename):
    doc = Document(filepath)
    lines = []
    img_count = 0
    for para in doc.paragraphs:
        t = para.text.strip()
        if t:
            lines.append(t)
    for ti, table in enumerate(doc.tables):
        lines.append(f"\n[表格 {ti+1}]")
        for row in table.rows:
            row_texts = []
            for cell in row.cells:
                ct = cell.text.strip().replace("\n", " ")
                row_texts.append(ct)
            lines.append(" | ".join(row_texts))
    try:
        with zipfile.ZipFile(filepath) as z:
            media_files = [n for n in z.namelist() if n.startswith("word/media/")]
            for idx, media_path in enumerate(media_files):
                img_data = z.read(media_path)
                if not img_data or len(img_data) < 100:
                    continue
                original_name = os.path.basename(media_path)
                ext = os.path.splitext(original_name)[1].lower()
                if ext not in ('.png', '.jpg', '.jpeg', '.gif', '.bmp', '.tiff', '.webp'):
                    ext = _guess_ext_from_bytes(img_data)
                img_name = f"{basename}_img{idx+1}{ext}"
                img_path = os.path.join(图片输出目录, img_name)
                with open(img_path, "wb") as f:
                    f.write(img_data)
                lines.append(f"[图片: {img_name}]")
                img_count += 1
    except Exception:
        pass

    return "\n".join(lines), len(doc.paragraphs), img_count

# ============================================================
# 5. 扫描并提取
# ============================================================
HANDLERS = {
    ".pdf":  extract_pdf,
    ".pptx": extract_pptx,
    ".pptm": extract_pptx,
    ".docx": extract_docx,
    ".dotx": extract_docx,
    ".dotm": extract_docx,
}

目标文件 = []
for fname in sorted(os.listdir(课件目录)):
    ext = os.path.splitext(fname)[1].lower()
    if ext in HANDLERS:
        目标文件.append(fname)

if not 目标文件:
    print(f"在 '{课件目录}' 中未找到支持的课件文件，请检查路径。")
    print(f"支持格式: {', '.join(sorted(set(HANDLERS.keys())))}")
    sys.exit(1)

print(f"找到 {len(目标文件)} 个课件文件，开始提取文本和图片...\n")

总图片数 = 0
成功 = 0
失败 = []
空内容 = []
纯图片文件 = []

for idx, fname in enumerate(目标文件, 1):
    filepath = os.path.join(课件目录, fname)
    ext = os.path.splitext(fname)[1].lower()
    basename = _sanitize_filename(Path(fname).stem)
    handler = HANDLERS[ext]

    # 预检：是否为纯图片文件
    if _check_likely_image_only(filepath, ext):
        纯图片文件.append(fname)
        print(f"  🔍 [{idx}/{len(目标文件)}] {fname} — 检测为纯图片型文件（扫描版PDF等），跳过文本提取")
        continue

    try:
        text, page_count, img_count = handler(filepath, basename)
        header = f"======= {fname} =======\n页数/幻灯片数: {page_count}\n" + "=" * 60
        if text.strip():
            outpath = os.path.join(文本输出目录, fname + ".txt")
            with open(outpath, "w", encoding="utf-8") as f:
                f.write(header + "\n" + text)
            成功 += 1
            总图片数 += img_count
            img_info = f", {img_count}张图片" if img_count else ""
            print(f"  ✓ [{成功}/{len(目标文件)}] {fname} ({page_count}p{img_info})")
        else:
            空内容.append(fname)
            print(f"  ⚠ [{成功}/{len(目标文件)}] {fname} — 提取内容为空")
    except Exception as e:
        失败.append((fname, str(e)))
        print(f"  ✗ [{成功}/{len(目标文件)}] {fname} — 错误: {e}")

# ============================================================
# 6. 结果报告
# ============================================================
print(f"\n{'=' * 50}")
print(f"提取完成: 成功 {成功}/{len(目标文件)}, 共提取 {总图片数} 张图片")
print(f"  文本目录: {os.path.abspath(文本输出目录)}")
print(f"  图片目录: {os.path.abspath(图片输出目录)}")

if 纯图片文件:
    print(f"\n🔍 以下 {len(纯图片文件)} 个文件被检测为纯图片型（扫描版PDF等）：")
    for fn in 纯图片文件:
        print(f"  - {fn}")
    print("这些文件将通过AI视觉能力直接读取，不依赖文本提取。")
    print("如果你的AI助手不支持图片识别，请参考以下方案：")
    print("  方案A: 更换为支持视觉的模型（如Claude Opus 4、GPT-4V）")
    print("  方案B: 安装MCP视觉服务器（如MiniMax MCP）")
    print("  方案C: 使用本地OCR工具（如Tesseract）预处理为文本")

if 空内容:
    print(f"\n⚠ 以下文件提取内容为空 ({len(空内容)}个):")
    for fn in 空内容:
        print(f"  - {fn}")
    print("可能原因：PPTX/DOCX只含图片不含文字，或PDF为扫描版。")
    print("建议：请看上方纯图片检测结果，对应文件将通过AI视觉处理。")

if 失败:
    print(f"\n✗ 以下文件提取失败 ({len(失败)}个):")
    for fn, err in 失败:
        print(f"  - {fn}: {err}")

if not 空内容 and not 失败 and not 纯图片文件:
    print("所有文件提取成功！")
```

### 2.2 运行提取

让用户运行 `python extract_course_materials.py`。

### 2.3 读取提取结果

提取成功后：

1. **逐一读取** `extracted_text/` 下所有 `.txt` 文件，理解全部课件内容
2. **浏览图片目录** `extracted_images/`，了解可用的图表资源
3. 对于内容较长的课件（>2000行），分段读取确保不遗漏

### 2.4 处理纯图片课件（扫描版PDF/图片型PPTX）

若脚本报告有纯图片文件，按以下 **降级策略** 处理：

**Level 1：尝试AI助手自带视觉能力**
直接读取原始PDF/PPTX/DOCX文件中的图片进行内容识别——大多数现代AI助手模型具备多模态视觉能力，可以直接从图片中读取公式和文字。

**Level 2：尝试MCP视觉服务器**
如果当前模型不支持视觉，检查是否有可用的MCP视觉工具（如 `mcp__MiniMax__understand_image` 或类似工具）。通过 `ListMcpResourcesTool` 查看可用MCP资源。

**Level 3：引导用户解决**
如果以上均不可用，告知用户当前环境无法识别图片内容，引导用户：
- **方案A**：切换到支持视觉的模型（如 Claude Opus 4、GPT-4V、Gemini Pro Vision）
- **方案B**：安装MCP视觉服务器（向用户推荐可用的MCP视觉服务器并帮助配置）
- **方案C**：使用OCR工具预处理（推荐 Tesseract + pdf2image：`pip install pytesseract pdf2image`）

对于其他需要识图的环节（如浏览提取出的图片），也遵循同样的三级降级策略。

---

## Phase 3：补充调研（可选但推荐）

### 3.1 搜索相关课程资源

在生成复习文档前，搜索以下高质量来源补充对课程内容的理解：

- **GitHub**：搜索相关课程的开放笔记、习题解答、复习资料（如 `"课程英文名" course notes`、`"课程英文名" exam review`）
- **Wikipedia**：查证关键概念的精确定义
- **学术网站**：搜寻相关教程、讲义补充

### 3.2 使用原则

- 补充调研**仅用于辅助理解**课程内容，不替代用户提供的课件
- 所有引用外部来源的内容必须在复习文档中标注出处
- 如果搜索到的内容与课件冲突，以课件为准
- 如果某些概念理解不确定，在文档中用HTML注释标注 `<!-- 待确认 -->`

---

## Phase 4：生成HTML复习文档

基于你对全部课件文本和图片的深入理解，生成**单个自包含HTML文件**。

### 4.1 生成前的思考清单

在动笔前，完成以下思考：

1. 这门课程的核心主线是什么？
2. 哪些概念是"基石"（后续概念依赖它）？
3. 哪些公式/定理是考试必考？
4. 学生在哪些地方最容易混淆？
5. 典型考题有哪几类？每类对应什么解题模板？
6. 哪些图片是关键图表？（必须引用到文档中）
7. 哪些公式在提取后不完整？（逐一核对）
8. 哪些推导步骤被省略了？（必须补全）
9. 哪些概念需要SVG示意图辅助理解？（课件原图不足或缺失的部分）

### 4.2 文档结构（必须包含8个部分）

```
1. 封面信息（frontmatter）：考试范围、形式、教师、教材
2. 📖 阅读指南：给不同基础学生的阅读路径建议
3. 📑 目录：可点击锚点导航
4. 第〇章：开始之前—课程核心思维（主线流程图、核心关系、学习动机）
5. 各章节精讲（第1章到第N章）：每章含概念精讲+完整推导+例题详解
6. 附录A：公式速查卡（按主题分类的公式表格）
7. 附录B：解题模板（标准题型的算法化步骤）
8. 附录C：常见错误与陷阱（易错点对照表）
```

### 4.3 HTML模板

生成的HTML必须基于以下模板，确保样式、数学渲染和打印支持。

你生成HTML文档时，将实际内容填入 `<!-- 文档内容 -->` 占位处。

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>[课程中文名] ([英文缩写]) [考试类型]复习完全指南</title>
<script>
window.MathJax = {
  tex: {
    inlineMath: [['$', '$'], ['\\(', '\\)']],
    displayMath: [['$$', '$$'], ['\\[', '\\]']],
    tags: 'ams'
  },
  svg: { fontCache: 'global' }
};
</script>
<script id="MathJax-script" async src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-svg.js"></script>
<style>
  /* ===== CSS Variables ===== */
  :root {
    --primary: #1a56db;
    --primary-light: #e8f0fe;
    --accent: #c41e3a;
    --accent-light: #fce4e8;
    --bg: #ffffff;
    --bg-soft: #f8fafc;
    --text: #1e293b;
    --text-muted: #64748b;
    --border: #e2e8f0;
    --shadow: 0 1px 3px rgba(0,0,0,0.08);
    --radius: 8px;
    --max-width: 960px;
    --font-body: system-ui, -apple-system, "Segoe UI", "Noto Sans SC", sans-serif;
    --font-mono: "JetBrains Mono", "Fira Code", "Cascadia Code", monospace;
  }

  /* ===== Reset & Base ===== */
  *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
  html { scroll-behavior: smooth; font-size: 16px; }
  body {
    font-family: var(--font-body);
    color: var(--text);
    background: var(--bg);
    line-height: 1.75;
    max-width: var(--max-width);
    margin: 0 auto;
    padding: 2rem 1.5rem 4rem;
  }

  /* ===== Typography ===== */
  h1 { font-size: 2rem; font-weight: 800; color: var(--primary); border-bottom: 3px solid var(--primary); padding-bottom: 0.5rem; margin: 2rem 0 1rem; }
  h2 { font-size: 1.5rem; font-weight: 700; color: var(--primary); margin: 2.5rem 0 1rem; padding-left: 0.5rem; border-left: 4px solid var(--primary); }
  h3 { font-size: 1.2rem; font-weight: 600; color: var(--text); margin: 1.8rem 0 0.8rem; }
  h4 { font-size: 1.05rem; font-weight: 600; color: var(--text-muted); margin: 1.2rem 0 0.5rem; }
  p { margin: 0.6rem 0; }
  a { color: var(--primary); text-decoration: none; }
  a:hover { text-decoration: underline; }

  /* ===== Blockquote (💡直觉理解) ===== */
  blockquote {
    border-left: 4px solid var(--primary);
    background: var(--primary-light);
    margin: 1rem 0;
    padding: 0.8rem 1rem;
    border-radius: 0 var(--radius) var(--radius) 0;
    color: #1e40af;
  }
  blockquote::before { content: "💡 "; font-weight: bold; }

  /* ===== Code ===== */
  code { font-family: var(--font-mono); background: var(--bg-soft); padding: 0.15em 0.4em; border-radius: 4px; font-size: 0.9em; }
  pre { background: #1e293b; color: #e2e8f0; padding: 1rem; border-radius: var(--radius); overflow-x: auto; margin: 1rem 0; }
  pre code { background: none; padding: 0; color: inherit; }

  /* ===== Tables ===== */
  table { width: 100%; border-collapse: collapse; margin: 1rem 0; font-size: 0.92rem; }
  th, td { border: 1px solid var(--border); padding: 0.6rem 0.8rem; text-align: left; }
  th { background: var(--primary); color: #fff; font-weight: 600; }
  tr:nth-child(even) { background: var(--bg-soft); }

  /* ===== Images ===== */
  img { max-width: 100%; height: auto; border-radius: var(--radius); box-shadow: var(--shadow); margin: 1rem 0; display: block; }
  figure { margin: 1.2rem 0; }
  figcaption { text-align: center; font-size: 0.88rem; color: var(--text-muted); margin-top: 0.3rem; }

  /* ===== SVG Diagrams ===== */
  .diagram-container { text-align: center; margin: 1.2rem 0; }
  .diagram-container svg { max-width: 100%; height: auto; }

  /* ===== Callout Boxes ===== */
  .callout {
    margin: 1rem 0; padding: 0.8rem 1rem; border-radius: var(--radius);
    border-left: 4px solid;
  }
  .callout-def     { background: #eff6ff; border-color: #3b82f6; } /* 📌 定义 */
  .callout-key     { background: #fef3c7; border-color: #f59e0b; } /* 🔑 关键关系 */
  .callout-derive  { background: #f0fdf4; border-color: #22c55e; } /* 📐 完整推导 */
  .callout-example { background: #fef2f2; border-color: #ef4444; } /* ✏️ 例题 */
  .callout-warn    { background: #fff7ed; border-color: #f97316; } /* ⚠️ 注意事项 */

  /* ===== Frontmatter Box ===== */
  .frontmatter {
    background: linear-gradient(135deg, var(--primary-light), #f0f4ff);
    border: 2px solid var(--primary);
    border-radius: var(--radius);
    padding: 1.2rem 1.5rem;
    margin: 1rem 0 2rem;
  }
  .frontmatter p { margin: 0.25rem 0; }

  /* ===== ToC ===== */
  .toc { background: var(--bg-soft); border: 1px solid var(--border); border-radius: var(--radius); padding: 1rem 1.5rem; margin: 1.5rem 0; }
  .toc h2 { margin-top: 0; border: none; padding: 0; }
  .toc ol { padding-left: 1.5rem; }
  .toc li { margin: 0.3rem 0; line-height: 1.6; }
  .toc ol ol { padding-left: 1.2rem; font-size: 0.92rem; }

  /* ===== Badges ===== */
  .badge { display: inline-block; padding: 0.15em 0.5em; border-radius: 12px; font-size: 0.82rem; font-weight: 600; }
  .badge-exam    { background: #fee2e2; color: #991b1b; }
  .badge-note    { background: #dbeafe; color: #1e40af; }
  .badge-optional{ background: #f3f4f6; color: #6b7280; }

  /* ===== Print Styles ===== */
  @media print {
    body { max-width: none; padding: 0.5in; font-size: 11pt; }
    h1 { font-size: 20pt; } h2 { font-size: 15pt; } h3 { font-size: 12pt; }
    .toc, .frontmatter, blockquote { break-inside: avoid; }
    img, svg, figure { break-inside: avoid; max-width: 90%; }
    a { color: var(--text); }
    pre { white-space: pre-wrap; }
  }

  /* ===== Responsive ===== */
  @media (max-width: 768px) {
    body { padding: 1rem 0.8rem 2rem; }
    h1 { font-size: 1.5rem; } h2 { font-size: 1.25rem; }
    table { font-size: 0.82rem; }
    th, td { padding: 0.4rem 0.5rem; }
  }
</style>
</head>
<body>

<!-- ===== 封面信息 ===== -->
<div class="frontmatter">
  <p><strong>📋 考试范围</strong>: [章节范围] | <strong>不考</strong>: [排除章节]</p>
  <p><strong>📝 考试形式</strong>: [开/闭]卷笔试 | <strong>教师</strong>: [姓名] | <strong>教材</strong>: [书名 版本]</p>
  <p><strong>📅 生成时间</strong>: [日期] | <strong>课件来源</strong>: [课件文件列表摘要]</p>
</div>

<!-- ===== 📖 阅读指南 ===== -->
<h2 id="reading-guide">📖 阅读指南</h2>
<blockquote>
  <strong>如果你基础薄弱，请按以下路径复习：</strong><br>
  1. 先快速浏览所有带 📌 标记的核心概念，无需深究细节<br>
  2. 重点理解 🔑 标记的关键关系和 📐 标记的完整推导<br>
  3. 动手做 ✏️ 标记的例题，做完再看解答<br>
  4. 最后用附录快速查漏补缺
</blockquote>

<!-- ===== 📑 目录 ===== -->
<div class="toc">
  <h2>📑 目录</h2>
  <ol>
    <li><a href="#ch0">第〇章：开始之前——课程核心思维</a></li>
    <!-- 各章节由你根据实际课件填充 -->
    <li><a href="#appendix-a">附录A：公式速查卡</a></li>
    <li><a href="#appendix-b">附录B：解题模板</a></li>
    <li><a href="#appendix-c">附录C：常见错误与陷阱</a></li>
  </ol>
</div>

<!-- ===== 第〇章：课程核心思维 ===== -->
<h2 id="ch0">第〇章：开始之前——课程核心思维</h2>

<h3>📌 [课程]的一条主线</h3>
<p>用SVG流程图展示课程核心主线：</p>
<div class="diagram-container">
  <!-- 内联SVG流程图 —— 由你生成 -->
</div>

<h3>🔑 最重要的关系</h3>
<p>课程最核心的1-3个定理/公式及它们之间的关系。</p>

<h3>📌 为什么要学这些？</h3>
<p>建立学习动机：这些知识解决什么实际问题。</p>

<!-- ============================================================ -->
<!-- ===== 第N章模板（为每一章复制此结构） ===== -->
<!-- ============================================================ -->

<h2 id="chN">第N章：[章节名] <span class="badge badge-note">[对应课件文件名]</span></h2>

<blockquote><strong>本章核心任务</strong>: [一句话概括本章在课程中的角色]</blockquote>

<!-- ===== N.M 小节 ===== -->
<h3 id="chN-M">📌 [概念中文名] ([English Term])</h3>

<div class="callout callout-def">
  <p>[精确的1-2句数学定义]</p>
  <p>$$[核心公式，置于 \boxed{} 中]$$</p>
</div>

<figure>
  <img src="extracted_images/[课件名]_pN_imgM.png" alt="[描述]">
  <figcaption>图 N.M：[说明该图表达的概念]（来源：[课件文件名]）</figcaption>
</figure>

<p><strong>意义</strong>: [这个概念在课程体系中的位置，解决什么问题]</p>

<blockquote><strong>直观理解</strong>：[用日常比喻或通俗语言解释这个概念]</blockquote>

<!-- 如果课件中推导有省略，补全完整推导 -->
<div class="callout callout-derive">
  <p>📐 <strong>推导：[定理/公式名]的完整推导</strong></p>
  <p>从 [起点公式/定义] 出发：</p>
  <p><strong>第1步</strong>：[操作描述——做了什么 + 为什么这样做]</p>
  <p>$$[中间表达式1]$$</p>
  <p><strong>第2步</strong>：[操作描述]</p>
  <p>$$[中间表达式2]$$</p>
  <p>……</p>
  <p><strong>最终结果</strong>：</p>
  <p>$$\boxed{[最终公式]}$$</p>
</div>

<!-- 如果需要SVG辅助解释推导过程，生成内联SVG -->
<div class="diagram-container">
  <!-- 推导步骤的可视化SVG —— 由你生成 -->
</div>

<p><strong>推导要点</strong>：总结推导中最关键的技巧或最容易出错的地方。</p>

<div class="callout callout-example">
  <p>✏️ <strong>例题</strong>：[题目描述]</p>
  <p><strong>解</strong>：</p>
  <p><strong>步骤1</strong>：[操作]</p>
  <p>$$[表达式]$$</p>
  <p><strong>步骤2</strong>：[操作]</p>
  <p>$$[表达式]$$</p>
  <p>……</p>
  <p>$$\boxed{[最终答案]}$$</p>
  <p><strong>易错点</strong>：[这道题最容易出错的地方]</p>
</div>

<p><strong>关联</strong>：[指向相关概念] → 见 <a href="#chX-Y">第X章 N.X节</a></p>

<!-- ============================================================ -->
<!-- ===== 附录A：公式速查卡 ===== -->
<!-- ============================================================ -->

<h2 id="appendix-a">附录A：公式速查卡</h2>

<h3>A1. [主题1]</h3>
<table>
  <tr><th>公式</th><th>名称</th><th>说明</th></tr>
  <tr><td>$$\boxed{[公式]}$$</td><td>[名称]</td><td>[一句话说明用途和条件]</td></tr>
</table>

<!-- ============================================================ -->
<!-- ===== 附录B：解题模板 ===== -->
<!-- ============================================================ -->

<h2 id="appendix-b">附录B：解题模板</h2>

<h3>B1. [题型名称]</h3>
<p><strong>适用场景</strong>: [什么时候用这个模板]</p>
<p><strong>解题步骤</strong>：</p>
<ol>
  <li><strong>[步骤名]</strong>：[具体操作]</li>
  <li><strong>[步骤名]</strong>：[具体操作]</li>
</ol>
<pre><code>[伪代码或Python代码——可选]</code></pre>

<!-- ============================================================ -->
<!-- ===== 附录C：常见错误 ===== -->
<!-- ============================================================ -->

<h2 id="appendix-c">附录C：常见错误与陷阱</h2>
<table>
  <tr><th>#</th><th>常见错误</th><th>为什么错</th><th>正确做法</th></tr>
  <tr>
    <td>1</td>
    <td>[学生常犯的错误]</td>
    <td>[错误的原因]</td>
    <td>[正确做法]</td>
  </tr>
</table>

<!-- ===== 页脚 ===== -->
<hr style="margin-top:3rem; border-color:var(--border);">
<p style="text-align:center; color:var(--text-muted); font-size:0.85rem;">
  本文档由 AI 助手基于课程课件自动生成 | [生成日期]<br>
  内容仅供参考，请以教材和教师授课为准
</p>

</body>
</html>
```

### 4.4 图片使用策略

#### 4.4.1 课件原图引用

在HTML中通过 `<img>` 标签引用提取的图片，使用相对路径：

```html
<figure>
  <img src="extracted_images/chapter1_L1_p3_img1.png" alt="[图像描述]">
  <figcaption>图 N.M：[说明]（来源：[课件名]）</figcaption>
</figure>
```

**必须引用的图片类型**：
- 核心概念示意图（系统框图、信号流程图、物理模型图）
- 关键公式的图解推导（几何解释、坐标变换示意图）
- 对比图（正确vs错误、变换前vs后）
- 解题流程图（算法步骤图、决策树）

**不引用的图片类型**：
- 纯装饰性图片
- 与文字完全重复的简单公式截图
- 分辨率过低无法辨认的图片

**每章至少引用3张课件原图，每个核心概念至少配1张示意图。**

#### 4.4.2 SVG示意图生成

当课件原图不足以清晰说明概念，或需要额外可视化辅助时，直接生成内联SVG。

**SVG适用场景**：
| 类型 | 用途 | 示例 |
|------|------|------|
| 流程图 | 课程结构、算法步骤、概念关系 | 课程主线流程图 |
| 框图 | 系统架构、信号流、组件交互 | 滤波器设计框图 |
| 坐标图 | 函数可视化、变换示意 | 傅里叶变换频谱示意 |
| 对比图 | 概念并排比较 | 连续vs离散信号对比 |
| 决策树 | 解题策略选择 | 选用哪种变换的判断流程 |

**SVG生成规范**：
- 直接嵌入HTML，不使用外部文件
- 使用 `<div class="diagram-container">` 包裹
- 配色与文档CSS变量一致（主色 `#1a56db`、强调色 `#c41e3a`）
- 包含清晰的标签和注释
- viewBox 设计确保在移动端和打印时均可读
- 使用语义化SVG元素（`<text>` 用于标签，`<g>` 用于分组）

### 4.5 公式还原与推导补全

#### 4.5.1 公式完整性检查

课件文本提取后，逐一检查每个公式：

| 问题类型 | 表现 | 修复方式 |
|---------|------|---------|
| 公式断裂 | 多行公式被拆碎、上下标错位 | 根据数学常识还原为完整LaTeX |
| 符号丢失 | 希腊字母、积分号、求和号变乱码或消失 | 根据上下文推断正确符号 |
| 分数线丢失 | `a/b` 应为 `\frac{a}{b}` | 改写为标准LaTeX分数 |
| 上下标错位 | `x2` 应为 `x^2` 或 `x_2` | 根据公式含义判断 |
| 矩阵混乱 | 元素排列错乱 | 根据数学规则重新排列 |
| 函数名错误 | `sin` 应为 `\sin` | 统一标准LaTeX函数名 |

**原则**：优先相信课件原意，交叉验证多处出现的同一公式，不确定处用 `<!-- 待确认 -->` 标注。

#### 4.5.2 推导步骤补全

课件中被跳过的推导必须补全：

| 课件写法 | 展开为 |
|---------|--------|
| "易证得..." | 完整证明过程，至少3-5步 |
| "显然..." | 明确写出"显然"背后的逻辑 |
| "由此可得..." | 写出具体代数操作 |
| "代入可得..." | 写出代入表达式和化简过程 |
| 只有结果无推导 | 从定义出发补全完整推导链 |

**补全优先级**：
- 🔴 必须补全：考试必考公式的推导、核心定理的推导
- 🟡 建议补全：例题计算步骤、概念间衔接推导
- 🟢 可选：纯代数化简每一步
- ⚪ 不需要：教材中已有完整推导（引用教材页码即可）

### 4.6 图标系统

在HTML中使用以下CSS类对应图标：

| 图标 | CSS类 | 含义 |
|------|-------|------|
| 📌 | `.callout-def` | 核心概念/定义 |
| 🔑 | `.callout-key` | 关键关系/定理 |
| 📐 | `.callout-derive` | 完整推导 |
| ✏️ | `.callout-example` | 例题 |
| 💡 | `blockquote` | 直观理解 |
| ⚠️ | `.callout-warn` | 注意事项/易错点 |

### 4.7 质量确保标准

生成文档时逐条自检：

1. **双语精确性**：所有关键技术术语同时给出中文和英文
2. **数学排版**：所有公式使用LaTeX，重要结果 `\boxed{}`
3. **公式完整性**：每个提取出的公式逐一检查，无断裂、无符号丢失
4. **推导补全**：所有被跳过的推导步骤已补全，每步有文字解释
5. **分层解释**：每个核心概念包含 定义→配图→直觉→推导→例题→关联
6. **图文并茂**：每章至少3张课件原图，每个核心概念至少1张示意图
7. **SVG补充**：课件原图不足处，用SVG示意图补充
8. **深度脚手架**：可层层深入——frontmatter→第0章→速览图标→精读章节→附录检索
9. **多遍阅读设计**：图标标记使读者可以快扫📌或逐章精读
10. **学生同理心**：对比表格、记忆口诀、日常比喻
11. **考试实用主义**：关键考点标注、附录B解题模板、附录C常见错误
12. **统一视觉语言**：一致的CSS类、标题层级、表格格式、块引用约定。

### 4.8 特殊场景处理

**数学公式密集课程**：优先公式准确性，核心定理推导100%补全，附录A格外详尽。

**概念记忆为主课程**：增加对比表格和SVG对比图，多用记忆口诀和思维导图SVG。

**编程/实践类课程**：解题模板包含代码块，附录B含代码模板，SVG侧重架构图和流程图。

**课件质量差/内容缺失**：如实标注不完整章节，不编造内容。缺失处标注 `<!-- 内容缺失：课件未涵盖 -->`。

**纯图片课件**：跳过文本提取，直接用AI视觉逐页读取。提取的图片既是文本来源也是配图资源。

---

## Phase 5：质量检查

生成HTML文档后，逐项自检：

- [ ] 文档包含完整的8部分结构（frontmatter→阅读指南→目录→第0章→各章节→附录ABC）
- [ ] 所有公式使用LaTeX，关键结果 `\boxed{}`
- [ ] 逐一核对每个公式的完整性——无断裂、符号丢失、上下标错位
- [ ] 课件中所有被跳过的推导均已补全，每步有文字解释
- [ ] 图标系统（📌🔑📐✏️💡）使用一致，对应的CSS类正确
- [ ] 每章至少3张课件原图，图片路径正确可访问
- [ ] 核心概念（📌标记）至少配1张示意图（原图或SVG）
- [ ] SVG示意图质量合格：配色一致、标签清晰、语义正确
- [ ] 关键术语均为中英双语
- [ ] 附录A按主题分类，包含课程所有核心公式
- [ ] 附录B至少3种解题模板
- [ ] 附录C至少5条常见错误
- [ ] 各章节标注对应课件来源
- [ ] 目录锚点链接与章节id一一对应
- [ ] MathJax CDN引用正确，HTML在浏览器中可正常渲染
- [ ] 移动端和打印样式均可用

---

## 输出

将生成的HTML保存为用户指定的文件名。

向用户报告文档统计：章节数、例题数、公式数（近似）、补全的推导数、引用课件图片数、生成SVG数、附录条目数。
