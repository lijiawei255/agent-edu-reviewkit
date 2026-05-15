---
name: course-review-guide
description: 将课程原始课件（PDF/PPTX/DOCX）转化为图文并茂的高质量HTML考试复习文档。当用户提到"整理复习文档"、"生成复习指南"、"课件转复习资料"、"考试复习"、"期末/期中复习"、"整理课程笔记"时触发此技能。适用于任何课程的复习文档生成。
---

# 课程复习文档生成器（HTML版）

## 概述

本技能将课程原始课件一键转化为高质量、结构化、图文并茂的**单文件HTML交互式考试复习文档**。输出包含MathJax数学排版、内联SVG示意图、课件原图、完整公式推导、例题详解、交互式学习组件（可折叠推导、选项卡视图、练习测验、术语闪卡、进度追踪）、答题模板和常见错误附录。**公式残缺处自动还原，推导跳跃处自动补全，确保基础薄弱的学生仅靠本文档即可高效复习。**

---

## 🔴 运行模式判断（执行任何操作前必须先判断）

**开始任何 Phase 1 操作前，必须先执行以下判断：**

```
第一步：检查课件目录是否存在 exam-scope.json 文件
  ↓
第二步：判断当前平台
  ↓
如果 (存在 exam-scope.json) OR (运行在 OpenClaw/Hermes 自主平台):
    → 进入【自主模式】流程（跳过用户询问，读取配置或自动推断）
否则:
    → 进入【交互式模式】流程（必须逐项询问用户确认考试范围）
```

**判断原则**：
- `exam-scope.json` 存在 = 自主模式（用户已预设范围，无需询问）
- OpenClaw/Hermes 平台 = 自主模式（无交互能力）
- **其他所有情况 = 交互式模式（必须询问用户）**

---

## Agent 平台说明

本技能支持多种 AI 编程助手和自主智能体平台。各平台适配详情见项目根目录的 `AGENTS.md`。

| 平台 | 优先级 | 配置文件 | 默认运行模式 |
|------|--------|----------|--------------|
| Claude Code | P0 | CLAUDE.md | **交互式模式**（必须询问用户） |
| Codex | P0 | 自定义 Prompt | **交互式模式**（必须询问用户） |
| OpenCode | P1 | AGENTS.md, opencode.json | **交互式模式**（必须询问用户） |
| OpenClaw/Hermes | P2 | AGENTS.md | 自主模式 |

### OpenCode 适配

运行 OpenCode 时：
1. **文件发现**：使用 `Glob` 而非 `Bash("ls ...")`
2. **图片识别**：直接尝试图片读取，不依赖 `ListMcpResourcesTool`
3. **Python 执行**：使用 `Bash("python3 ...")`，优先使用 `python3`
4. **用户交互**：OpenCode 支持完整交互式会话，Phase 1 范围确认按原流程执行
5. **文件写入**：使用 `Write` 工具

### OpenClaw / Hermes 适配（自主模式）

作为自主 agent 运行时，**不能等待交互式用户响应**：

1. **范围确定**：首先检查课件目录中是否有 `exam-scope.json`。如找到，读取所有值跳过交互确认。如未找到，从文件名和内容推断范围，所有推断值标注 `[自动推断 - 请验证]`。
2. **渐进式失败**：一个阶段失败时，生成已完成部分并标注缺失，而非完全停止。
3. **输出信令**：完成后输出源文件列表、推断/配置的范围、待验证项、不完整章节。
4. **无交互暂停**：使用"检查是否存在"、"推断自"替代"询问用户"。
5. **范围配置模板**：如未找到 `exam-scope.json`，在课件目录自动生成 `exam-scope-template.json`（含推断默认值），供用户下次填写。
6. **自主模式横幅**：HTML 文档顶部插入醒目横幅，提醒用户考试范围为自动推断。

---

## Phase 1：信息收集与范围确认

**⚠️ 开始前必须已完成【运行模式判断】，确认是交互式还是自主模式**

---

### 分支 A：交互式模式（Claude Code / Codex / OpenCode）

**必须逐项询问用户，不得跳过或自动推断**

#### A1. 确认课件位置

向用户询问课件文件所在的目录路径。如果用户未提供，请用户将所有课件文件放入一个目录。

#### A2. 扫描课件文件

使用 Glob 或 Bash（`ls`）扫描课件目录，列出所有 `.pdf`、`.pptx`、`.docx` 文件及其变体（`.pptm`、`.dotx`、`.dotm`），以表格呈现文件名和大小。

#### A3. 确认考试范围（🔴 必须询问，不得跳过）

逐项向用户确认以下信息，除非用户明确表示"使用默认值"或"全部覆盖"：

1. **考试范围**：哪些章节/讲座在考试范围内？哪些明确不考？
2. **课程全称**：中文全称和英文全称
3. **授课教师**：姓名和单位（如有）
4. **参考教材**：书名、作者、版本（如有）
5. **考试形式**：闭卷/开卷/半开卷
6. **授课语言**：中文/英文/双语
7. **输出文件名**：期望的 `.html` 输出文件名
8. **是否需要押题文档**：是/否，以及输出方式（追加/独立文件）

#### A4. 创建输出目录

在课件目录下创建 `extracted_text/` 和 `extracted_images/`。

---

### 分支 B：自主模式（OpenClaw / Hermes / 存在 exam-scope.json）

**跳过用户询问，按以下流程自动执行**

#### B1. 扫描课件文件

使用 Glob 扫描课件目录，列出所有课件文件。

#### B2. 读取或推断考试范围

1. 如存在 `exam-scope.json`：读取所有配置值
2. 如不存在：从文件名和内容推断范围，所有推断值标注 `[自动推断 - 请验证]`
3. 在课件目录生成 `exam-scope-template.json`（含推断默认值），供用户下次填写

#### B3. 创建输出目录

在课件目录下创建 `extracted_text/` 和 `extracted_images/`。

---

## Phase 2：课件内容提取

### 2.1 准备提取脚本

将项目根目录中的 `extract_course_materials.py` 复制到你的课件目录下。

打开 `extract_course_materials.py`，修改第49-53行的配置区路径：
- `课件目录`：你的课件所在目录
- `文本输出目录`：提取文本的输出目录（默认为 `extracted_text`）
- `图片输出目录`：提取图片的输出目录（默认为 `extracted_images`）

**功能说明**：
- 支持 `.pdf`、`.pptx`/`.pptm`、`.docx`/`.dotx`/`.dotm` 格式
- 自动检测纯图片型课件（扫描版PDF）并跳过文本提取
- 自动过滤不兼容浏览器的 EMF/WMF 格式图片
- 在提取文本中用 `[图片: xxx.png]` 标记图片位置
- 最后输出详细的提取统计报告

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
<script id="MathJax-script" async src="./mathjax/es5/tex-svg.js"
        onerror="
          var cdn=document.createElement('script');
          cdn.id='MathJax-script';cdn.async=true;
          cdn.src='https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-svg.js';
          this.remove();document.head.appendChild(cdn);
        "></script>
<noscript>
  <p style="color: #c41e3a; text-align: center; padding: 1rem; border: 2px dashed #c41e3a;">
    ⚠ 此文档需要 JavaScript 才能正确渲染数学公式。请启用 JavaScript 或使用现代浏览器打开。
  </p>
</noscript>
<style>
  /* ===== CSS Variables ===== */
  :root {
    --primary: #2563eb;
    --primary-dark: #1d4ed8;
    --primary-light: #eff6ff;
    --secondary: #d97706;
    --secondary-light: #fffbeb;
    --accent: #dc2626;
    --accent-light: #fef2f2;
    --bg: #ffffff;
    --bg-soft: #f8fafc;
    --bg-card: #ffffff;
    --text: #334155;
    --text-heading: #1e293b;
    --text-muted: #64748b;
    --border: #e2e8f0;
    --shadow-sm: 0 1px 2px rgba(0,0,0,0.05);
    --shadow: 0 1px 3px rgba(0,0,0,0.1), 0 1px 2px rgba(0,0,0,0.06);
    --shadow-md: 0 4px 6px rgba(0,0,0,0.07), 0 2px 4px rgba(0,0,0,0.06);
    --radius: 8px;
    --radius-lg: 12px;
    --max-width: 960px;
    --toc-width: 240px;
    --font-body: system-ui, -apple-system, "Segoe UI", "Noto Sans SC", "PingFang SC", "Microsoft YaHei", sans-serif;
    --font-mono: "JetBrains Mono", "Fira Code", "Cascadia Code", "Consolas", monospace;
  }

  /* ===== Reset & Base ===== */
  *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
  html { scroll-behavior: smooth; font-size: 16px; }
  body {
    font-family: var(--font-body);
    color: var(--text);
    background: #f1f5f9;
    line-height: 1.8;
    letter-spacing: -0.01em;
    text-wrap: pretty;
  }

  /* ===== Hero Header ===== */
  .hero {
    background: linear-gradient(135deg, #1e40af 0%, #3b82f6 40%, #6366f1 100%);
    color: #fff;
    padding: 3rem 2rem;
    margin-bottom: 2rem;
    text-align: center;
  }
  .hero h1 {
    font-size: 2.5rem;
    font-weight: 800;
    color: #fff;
    margin: 0 0 0.75rem;
    letter-spacing: -0.02em;
    border: none;
    padding: 0;
  }
  .hero .hero-subtitle {
    font-size: 1.1rem;
    opacity: 0.85;
    margin-bottom: 1.5rem;
  }
  .hero .meta-card {
    display: inline-flex;
    flex-wrap: wrap;
    gap: 0.5rem 1.5rem;
    background: rgba(255,255,255,0.12);
    backdrop-filter: blur(8px);
    border-radius: var(--radius-lg);
    padding: 1rem 1.5rem;
    font-size: 0.9rem;
    text-align: left;
    justify-content: center;
  }
  .hero .meta-card .meta-item {
    white-space: nowrap;
  }
  .hero .meta-card strong {
    color: rgba(255,255,255,0.7);
    font-weight: 500;
  }

  /* ===== Page wrapper (for sticky ToC on wide screens) ===== */
  .page-wrapper {
    max-width: calc(var(--max-width) + var(--toc-width) + 3rem);
    margin: 0 auto;
    padding: 0 1.5rem 4rem;
    display: flex;
    gap: 2rem;
    align-items: flex-start;
  }

  /* ===== Sticky ToC ===== */
  .toc-sidebar {
    position: sticky;
    top: 1rem;
    width: var(--toc-width);
    flex-shrink: 0;
    background: var(--bg);
    border: 1px solid var(--border);
    border-radius: var(--radius-lg);
    padding: 1.2rem 1rem;
    box-shadow: var(--shadow-sm);
    max-height: calc(100vh - 2rem);
    overflow-y: auto;
    font-size: 0.88rem;
    display: none;
  }
  @media (min-width: 1200px) {
    .toc-sidebar { display: block; }
  }
  .toc-sidebar h2 {
    font-size: 1rem;
    margin: 0 0 0.75rem;
    border: none;
    padding: 0;
    color: var(--text-heading);
  }
  .toc-sidebar ol { padding-left: 1.2rem; list-style: none; }
  .toc-sidebar li { margin: 0.25rem 0; line-height: 1.5; }
  .toc-sidebar a { color: var(--text-muted); text-decoration: none; transition: color 0.15s; }
  .toc-sidebar a:hover { color: var(--primary); }
  .toc-sidebar ol ol { padding-left: 0.8rem; font-size: 0.82rem; }
  .toc-sidebar ol ol li { margin: 0.15rem 0; }

  /* ===== Main content column ===== */
  .main-content {
    flex: 1;
    min-width: 0;
  }

  /* ===== Hero-header ToC (mobile fallback) ===== */
  .toc-inline {
    background: var(--bg-soft);
    border: 1px solid var(--border);
    border-radius: var(--radius-lg);
    padding: 1rem 1.5rem;
    margin: 1.5rem 0;
  }
  @media (min-width: 1200px) {
    .toc-inline { display: none; }
  }
  .toc-inline h2 { margin-top: 0; border: none; padding: 0; font-size: 1.1rem; }
  .toc-inline ol { padding-left: 1.5rem; }
  .toc-inline li { margin: 0.3rem 0; line-height: 1.6; }
  .toc-inline ol ol { padding-left: 1.2rem; font-size: 0.92rem; }

  /* ===== Typography ===== */
  h1 {
    font-size: 2.2rem;
    font-weight: 800;
    color: var(--primary-dark);
    border-bottom: 2px solid var(--border);
    padding-bottom: 0.5rem;
    margin: 2.5rem 0 1rem;
    letter-spacing: -0.015em;
  }
  h2 {
    font-size: 1.65rem;
    font-weight: 700;
    color: var(--text-heading);
    margin: 2.5rem 0 1rem;
    padding-left: 0.75rem;
    border-left: 4px solid var(--primary);
  }
  h3 { font-size: 1.2rem; font-weight: 600; color: var(--text-heading); margin: 1.8rem 0 0.8rem; }
  h4 { font-size: 1.05rem; font-weight: 600; color: var(--text-muted); margin: 1.2rem 0 0.5rem; }
  p { margin: 0.7rem 0; }
  a { color: var(--primary); text-decoration: none; }
  a:hover { text-decoration: underline; }

  /* ===== Chapter Cards ===== */
  .chapter-card {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: var(--radius-lg);
    box-shadow: var(--shadow-sm);
    padding: 1.5rem 2rem;
    margin: 2rem 0;
    transition: box-shadow 0.2s;
  }
  .chapter-card:hover { box-shadow: var(--shadow); }
  .chapter-card h2 {
    margin-top: 0;
    border: none;
    padding-left: 0;
  }

  /* ===== Blockquote (💡直觉理解) ===== */
  blockquote {
    border-left: 4px solid var(--primary);
    background: var(--primary-light);
    margin: 1.2rem 0;
    padding: 1rem 1.2rem;
    border-radius: 0 var(--radius-lg) var(--radius-lg) 0;
    color: #1e40af;
  }
  blockquote::before { content: "💡 "; font-weight: bold; }

  /* ===== Code ===== */
  code { font-family: var(--font-mono); background: var(--bg-soft); padding: 0.15em 0.4em; border-radius: 4px; font-size: 0.9em; }
  pre { background: #1e293b; color: #e2e8f0; padding: 1.2rem; border-radius: var(--radius-lg); overflow-x: auto; margin: 1rem 0; line-height: 1.6; }
  pre code { background: none; padding: 0; color: inherit; }

  /* ===== Tables ===== */
  table { width: 100%; border-collapse: collapse; margin: 1.2rem 0; font-size: 0.92rem; border-radius: var(--radius-lg); overflow: hidden; box-shadow: var(--shadow-sm); }
  th, td { border: 1px solid var(--border); padding: 0.7rem 0.9rem; text-align: left; }
  th { background: var(--primary); color: #fff; font-weight: 600; }
  tr:nth-child(even) { background: var(--bg-soft); }

  /* ===== Images ===== */
  img {
    max-width: 100%;
    height: auto;
    border-radius: var(--radius-lg);
    box-shadow: var(--shadow);
    margin: 1.2rem 0;
    display: block;
    border: 1px solid var(--border);
    transition: transform 0.2s ease;
  }
  img:hover { transform: scale(1.01); }
  figure { margin: 1.5rem 0; }
  figcaption { text-align: center; font-size: 0.88rem; color: var(--text-muted); margin-top: 0.4rem; }

  /* ===== SVG Diagrams ===== */
  .diagram-container { text-align: center; margin: 1.5rem 0; padding: 1rem; background: var(--bg-soft); border-radius: var(--radius-lg); }
  .diagram-container svg { max-width: 100%; height: auto; }

  /* ===== Callout Boxes (with gradient left accent) ===== */
  .callout {
    margin: 1.2rem 0;
    padding: 1rem 1.2rem;
    border-radius: var(--radius-lg);
    border-left: 5px solid;
    box-shadow: var(--shadow-sm);
  }
  .callout-def     { background: #eff6ff; border-color: #3b82f6; } /* 📌 定义 */
  .callout-key     { background: #fffbeb; border-color: #d97706; } /* 🔑 关键关系 */
  .callout-derive  { background: #f0fdf4; border-color: #16a34a; } /* 📐 完整推导 */
  .callout-example { background: #fef2f2; border-color: #dc2626; } /* ✏️ 例题 */
  .callout-warn    { background: #fff7ed; border-color: #ea580c; } /* ⚠️ 注意事项 */

  /* ===== Badges ===== */
  .badge { display: inline-block; padding: 0.2em 0.6em; border-radius: 12px; font-size: 0.82rem; font-weight: 600; }
  .badge-exam    { background: #fee2e2; color: #991b1b; }
  .badge-note    { background: #dbeafe; color: #1e40af; }
  .badge-optional{ background: #f3f4f6; color: #6b7280; }
  .badge-important { background: #fef3c7; color: #92400e; }

  /* ===== MathJax formula breathing room ===== */
  mjx-container {
    padding: 0.15rem 0;
  }

  /* ===== Footer ===== */
  .page-footer {
    text-align: center;
    color: var(--text-muted);
    font-size: 0.85rem;
    margin-top: 3rem;
    padding-top: 1.5rem;
    border-top: 1px solid var(--border);
  }

  /* ===== Print Styles ===== */
  @media print {
    body { background: #fff; }
    .hero { background: #fff !important; color: #000; border-bottom: 3px solid #000; padding: 1rem 0; }
    .hero h1 { color: #000; }
    .hero .meta-card { background: #f5f5f5; border: 1px solid #ccc; color: #000; }
    .hero .meta-card strong { color: #555; }
    .toc-sidebar { display: none; }
    .toc-inline { border: 1px solid #ccc; background: #fff; }
    .page-wrapper { max-width: none; padding: 0; display: block; }
    .main-content { max-width: none; }
    .chapter-card { box-shadow: none; border: 1px solid #ccc; break-inside: avoid; page-break-before: always; }
    .callout { box-shadow: none; break-inside: avoid; }
    img, svg, figure { break-inside: avoid; max-width: 90%; }
    img:hover { transform: none; }
    a { color: var(--text); }
    pre { white-space: pre-wrap; }
    h1 { font-size: 20pt; } h2 { font-size: 15pt; } h3 { font-size: 12pt; }
    details.derive-steps { display: block; }
    details.derive-steps > summary::before { display: none; }
    details.derive-steps > .derive-content { display: block; padding: 0; border: none; }
    .tab-buttons { display: none; }
    .tab-panel { display: block !important; }
    .quiz-section { border: 1px solid #ccc; background: #fff; }
    details.quiz-answer > .answer-content { display: block; }
    .flashcard { perspective: none; height: auto; break-inside: avoid; }
    .flashcard-inner { transform: none !important; transform-style: flat; }
    .flashcard-front, .flashcard-back { position: relative; backface-visibility: visible; }
    .flashcard-back { transform: none; margin-top: 0.5rem; }
    .progress-tracker { display: none; }
    .search-container { display: none; }
  }

  /* ===== Interactive: Collapsible Derivation Steps ===== */
  details.derive-steps {
    margin: 1rem 0;
    border: 1px solid var(--border);
    border-radius: var(--radius);
    background: var(--bg-soft);
  }
  details.derive-steps > summary {
    padding: 0.8rem 1rem;
    font-weight: 600;
    cursor: pointer;
    color: var(--primary);
    list-style: none;
    display: flex;
    align-items: center;
    gap: 0.5rem;
    user-select: none;
  }
  details.derive-steps > summary::before {
    content: "▶";
    font-size: 0.75rem;
    transition: transform 0.2s;
  }
  details.derive-steps[open] > summary::before {
    transform: rotate(90deg);
  }
  details.derive-steps > .derive-content {
    padding: 0.5rem 1rem 1rem;
    border-top: 1px solid var(--border);
  }

  /* ===== Interactive: Tabbed Content ===== */
  .tab-container { margin: 1.5rem 0; }
  .tab-buttons { display: flex; gap: 0; border-bottom: 2px solid var(--border); }
  .tab-btn {
    padding: 0.6rem 1.2rem;
    background: none;
    border: none;
    cursor: pointer;
    font-size: 0.92rem;
    font-weight: 600;
    color: var(--text-muted);
    border-bottom: 2px solid transparent;
    margin-bottom: -2px;
    transition: color 0.2s, border-color 0.2s;
    font-family: var(--font-body);
  }
  .tab-btn.active { color: var(--primary); border-bottom-color: var(--primary); }
  .tab-panel { display: none; padding: 1rem 0; }
  .tab-panel.active { display: block; }

  /* ===== Interactive: Quiz ===== */
  .quiz-section {
    margin: 2rem 0;
    border: 2px solid var(--primary-light);
    border-radius: var(--radius-lg);
    padding: 1.5rem;
    background: #fafbff;
  }
  .quiz-section h3 { color: var(--primary); }
  .quiz-item {
    margin: 1rem 0;
    padding: 1rem;
    background: var(--bg);
    border-radius: var(--radius);
    border: 1px solid var(--border);
  }
  details.quiz-answer { margin-top: 0.8rem; }
  details.quiz-answer > summary {
    cursor: pointer;
    font-weight: 600;
    color: var(--secondary);
    user-select: none;
    padding: 0.3rem 0;
  }
  details.quiz-answer > .answer-content {
    padding: 0.8rem 1rem;
    margin-top: 0.5rem;
    background: var(--secondary-light);
    border-radius: var(--radius);
  }

  /* ===== Interactive: Flashcard ===== */
  .flashcard-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
    gap: 1rem;
    margin: 1.5rem 0;
  }
  .flashcard {
    perspective: 600px;
    height: 160px;
    cursor: pointer;
  }
  .flashcard-inner {
    position: relative;
    width: 100%;
    height: 100%;
    transition: transform 0.5s;
    transform-style: preserve-3d;
  }
  .flashcard.flipped .flashcard-inner { transform: rotateY(180deg); }
  .flashcard-front, .flashcard-back {
    position: absolute;
    width: 100%;
    height: 100%;
    backface-visibility: hidden;
    border-radius: var(--radius);
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 1rem;
    text-align: center;
    font-size: 0.95rem;
  }
  .flashcard-front {
    background: var(--primary-light);
    border: 2px solid var(--primary);
    color: var(--primary-dark);
    font-weight: 700;
  }
  .flashcard-back {
    background: var(--secondary-light);
    border: 2px solid var(--secondary);
    transform: rotateY(180deg);
    font-size: 0.88rem;
  }

  /* ===== Interactive: Progress Tracker ===== */
  .progress-tracker {
    margin-bottom: 1rem;
    padding-bottom: 1rem;
    border-bottom: 1px solid var(--border);
  }
  .progress-bar-container {
    background: var(--bg-soft);
    border-radius: 20px;
    height: 8px;
    margin: 0.5rem 0;
    overflow: hidden;
  }
  .progress-bar-fill {
    height: 100%;
    background: linear-gradient(90deg, var(--primary), #6366f1);
    border-radius: 20px;
    width: 0%;
    transition: width 0.4s ease;
  }
  .progress-text {
    font-size: 0.85rem;
    color: var(--text-muted);
    text-align: center;
  }
  .section-checkbox {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    font-size: 0.88rem;
    margin: 0.3rem 0;
    cursor: pointer;
  }
  .section-checkbox input[type="checkbox"] {
    accent-color: var(--primary);
    width: 1rem;
    height: 1rem;
  }

  /* ===== Interactive: Search ===== */
  .search-container { margin: 1rem 0 1.5rem; position: relative; }
  .search-input {
    width: 100%;
    padding: 0.6rem 1rem 0.6rem 2.2rem;
    border: 1px solid var(--border);
    border-radius: var(--radius);
    font-size: 0.92rem;
    font-family: var(--font-body);
    background: var(--bg);
    transition: border-color 0.2s;
  }
  .search-input:focus { outline: none; border-color: var(--primary); }
  .search-icon {
    position: absolute;
    left: 0.7rem;
    top: 50%;
    transform: translateY(-50%);
    color: var(--text-muted);
    font-size: 0.9rem;
    pointer-events: none;
  }

  /* ===== Autonomous Mode Banner ===== */
  .autonomous-banner {
    background: linear-gradient(90deg, #fef3c7, #fde68a);
    border: 2px solid #f59e0b;
    border-radius: var(--radius-lg);
    padding: 1rem 1.5rem;
    margin: 1rem 0;
    text-align: center;
  }

  /* ===== Responsive ===== */
  @media (max-width: 768px) {
    .hero { padding: 2rem 1rem; }
    .hero h1 { font-size: 1.6rem; }
    .hero .meta-card { padding: 0.75rem 1rem; gap: 0.25rem 1rem; font-size: 0.82rem; }
    .page-wrapper { padding: 0 0.8rem 2rem; display: block; }
    .chapter-card { padding: 1rem 1.2rem; }
    h1 { font-size: 1.5rem; } h2 { font-size: 1.25rem; }
    table { font-size: 0.82rem; }
    th, td { padding: 0.4rem 0.5rem; }
  }
</style>
</head>
<body>

<!-- ===== Hero 封面 ===== -->
<header class="hero">
  <h1>[课程中文名] 复习完全指南</h1>
  <p class="hero-subtitle">[英文课程名] · [考试类型]考试</p>
  <div class="meta-card">
    <span class="meta-item"><strong>📋 考试范围</strong> [章节范围]</span>
    <span class="meta-item"><strong>🚫 不考</strong> [排除章节]</span>
    <span class="meta-item"><strong>📝 形式</strong> [开/闭]卷笔试</span>
    <span class="meta-item"><strong>👨‍🏫 教师</strong> [姓名]</span>
    <span class="meta-item"><strong>📚 教材</strong> [书名]</span>
    <span class="meta-item"><strong>📅 生成时间</strong> [日期]</span>
  </div>
</header>

<div class="page-wrapper">

<!-- ===== 侧边栏目录（宽屏固定）===== -->
<nav class="toc-sidebar">
  <h2>📑 目录</h2>
  <div class="progress-tracker">
    <div class="progress-bar-container"><div class="progress-bar-fill"></div></div>
    <div class="progress-text">0/N sections completed (0%)</div>
  </div>
  <ol>
    <li><label class="section-checkbox"><input type="checkbox" data-section="reading-guide"><a href="#reading-guide">📖 阅读指南</a></label></li>
    <li><label class="section-checkbox"><input type="checkbox" data-section="ch0"><a href="#ch0">第〇章：课程核心思维</a></label></li>
    <!-- 各章节由你根据实际课件填充，每项使用 section-checkbox 格式 -->
    <li><label class="section-checkbox"><input type="checkbox" data-section="appendix-a"><a href="#appendix-a">附录A：公式速查卡</a></label></li>
    <li><label class="section-checkbox"><input type="checkbox" data-section="appendix-b"><a href="#appendix-b">附录B：解题模板</a></label></li>
    <li><label class="section-checkbox"><input type="checkbox" data-section="appendix-c"><a href="#appendix-c">附录C：常见错误与陷阱</a></label></li>
  </ol>
</nav>

<main class="main-content">

<!-- ===== 🔍 搜索栏 ===== -->
<div class="search-container">
  <span class="search-icon">🔍</span>
  <input type="text" class="search-input" placeholder="搜索概念、公式、术语...">
</div>

<!-- ===== 自主模式横幅（仅自主 agent 生成时包含）===== -->
<!-- <div class="autonomous-banner">
  <strong>⚠ 此文档由自主代理自动生成</strong><br>
  考试范围为自动推断，<strong>请仔细核对</strong>以下信息是否正确。<br>
  <span style="font-size: 0.85rem; color: #92400e;">如需修正，请编辑课件目录中的 <code>exam-scope.json</code> 后重新生成。</span>
</div> -->

<!-- ===== 📖 阅读指南 ===== -->
<h2 id="reading-guide">📖 阅读指南</h2>
<blockquote>
  <strong>如果你基础薄弱，请按以下路径复习：</strong><br>
  1. 先快速浏览所有带 📌 标记的核心概念，无需深究细节<br>
  2. 重点理解 🔑 标记的关键关系和 📐 标记的完整推导<br>
  3. 动手做 ✏️ 标记的例题，做完再看解答<br>
  4. 最后用附录快速查漏补缺
</blockquote>

<!-- ===== 📑 目录（窄屏内联）===== -->
<div class="toc-inline">
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
<div class="chapter-card">
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
</div>

<!-- ============================================================ -->
<!-- ===== 第N章模板（为每一章复制此结构，每章一个 .chapter-card）===== -->
<!-- ============================================================ -->

<div class="chapter-card">
<h2 id="chN">第N章：[章节名] <span class="badge badge-note">[对应课件文件名]</span></h2>

<blockquote><strong>本章核心任务</strong>: [一句话概括本章在课程中的角色]</blockquote>

<!-- ===== 选项卡：快速复习 / 详细讲解 ===== -->
<div class="tab-container">
  <div class="tab-buttons">
    <button class="tab-btn active">⚡ 快速复习</button>
    <button class="tab-btn">📖 详细讲解</button>
  </div>

  <!-- ===== 快速复习面板 ===== -->
  <div class="tab-panel active">
    <p><strong>章节概要</strong>：[2-3句话概括本章要点]</p>

    <!-- 术语闪卡 -->
    <div class="flashcard-grid">
      <div class="flashcard" onclick="this.classList.toggle('flipped')">
        <div class="flashcard-inner">
          <div class="flashcard-front">[术语/概念名]</div>
          <div class="flashcard-back">[一句话定义或核心公式]</div>
        </div>
      </div>
      <!-- 每个核心概念一张闪卡，每章至少3-5张 -->
    </div>

    <h3>🔑 本章关键公式</h3>
    <table>
      <tr><th>公式</th><th>名称</th><th>说明</th></tr>
      <tr><td>$$\boxed{[公式]}$$</td><td>[名称]</td><td>[一句话说明]</td></tr>
    </table>
  </div>

  <!-- ===== 详细讲解面板 ===== -->
  <div class="tab-panel">

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

<!-- 可折叠推导步骤 -->
<details class="derive-steps">
  <summary>📐 推导：[定理/公式名]的完整推导</summary>
  <div class="derive-content">
    <p>从 [起点公式/定义] 出发：</p>
    <p><strong>第1步</strong>：[操作描述——做了什么 + 为什么这样做]</p>
    <p>$$[中间表达式1]$$</p>
    <p><strong>第2步</strong>：[操作描述]</p>
    <p>$$[中间表达式2]$$</p>
    <p>……</p>
    <p><strong>最终结果</strong>：</p>
    <p>$$\boxed{[最终公式]}$$</p>
  </div>
</details>

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

  </div><!-- .tab-panel 详细讲解 -->
</div><!-- .tab-container -->

<!-- ===== 练习测验 ===== -->
<div class="quiz-section">
  <h3>📝 练习检测</h3>
  <div class="quiz-item">
    <p><strong>Q1.</strong> [概念检查题]</p>
    <details class="quiz-answer">
      <summary>显示答案</summary>
      <div class="answer-content">
        <p>[答案及解析]</p>
      </div>
    </details>
  </div>
  <!-- 每章2-4道练习题 -->
</div>

</div>

<!-- ============================================================ -->
<!-- ===== 附录A：公式速查卡 ===== -->
<!-- ============================================================ -->

<div class="chapter-card">
<h2 id="appendix-a">附录A：公式速查卡</h2>

<h3>A1. [主题1]</h3>
<table>
  <tr><th>公式</th><th>名称</th><th>说明</th></tr>
  <tr><td>$$\boxed{[公式]}$$</td><td>[名称]</td><td>[一句话说明用途和条件]</td></tr>
</table>
</div>

<!-- ============================================================ -->
<!-- ===== 附录B：解题模板 ===== -->
<!-- ============================================================ -->

<div class="chapter-card">
<h2 id="appendix-b">附录B：解题模板</h2>

<h3>B1. [题型名称]</h3>
<p><strong>适用场景</strong>: [什么时候用这个模板]</p>
<p><strong>解题步骤</strong>：</p>
<ol>
  <li><strong>[步骤名]</strong>：[具体操作]</li>
  <li><strong>[步骤名]</strong>：[具体操作]</li>
</ol>
<pre><code>[伪代码或Python代码——可选]</code></pre>
</div>

<!-- ============================================================ -->
<!-- ===== 附录C：常见错误 ===== -->
<!-- ============================================================ -->

<div class="chapter-card">
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
</div>

<!-- ===== 页脚 ===== -->
<div class="page-footer">
  <p>本文档由 AI 助手基于课程课件自动生成 | [生成日期]<br>
  内容仅供参考，请以教材和教师授课为准</p>
</div>

</main><!-- .main-content -->
</div><!-- .page-wrapper -->

<script>
// === Tab Switching ===
document.querySelectorAll('.tab-container').forEach(function(container) {
  var buttons = container.querySelectorAll('.tab-btn');
  var panels = container.querySelectorAll('.tab-panel');
  buttons.forEach(function(btn, i) {
    btn.addEventListener('click', function() {
      buttons.forEach(function(b) { b.classList.remove('active'); });
      panels.forEach(function(p) { p.classList.remove('active'); });
      btn.classList.add('active');
      panels[i].classList.add('active');
    });
  });
});

// === Flashcard Flip ===
document.querySelectorAll('.flashcard').forEach(function(card) {
  card.addEventListener('click', function() {
    card.classList.toggle('flipped');
  });
});

// === Progress Tracker ===
(function() {
  var checkboxes = document.querySelectorAll('.section-checkbox input[type="checkbox"]');
  var total = checkboxes.length;
  var fill = document.querySelector('.progress-bar-fill');
  var text = document.querySelector('.progress-text');
  function updateProgress() {
    var checked = document.querySelectorAll('.section-checkbox input:checked').length;
    var pct = total > 0 ? Math.round((checked / total) * 100) : 0;
    if (fill) fill.style.width = pct + '%';
    if (text) text.textContent = checked + '/' + total + ' sections completed (' + pct + '%)';
    try {
      var state = {};
      checkboxes.forEach(function(cb, i) { state['sec_' + i] = cb.checked; });
      localStorage.setItem('review_progress_' + location.pathname, JSON.stringify(state));
    } catch(e) {}
  }
  try {
    var saved = JSON.parse(localStorage.getItem('review_progress_' + location.pathname) || '{}');
    checkboxes.forEach(function(cb, i) { if (saved['sec_' + i]) cb.checked = true; });
  } catch(e) {}
  checkboxes.forEach(function(cb) { cb.addEventListener('change', updateProgress); });
  updateProgress();
})();

// === Search/Filter ===
(function() {
  var input = document.querySelector('.search-input');
  if (!input) return;
  var mainContent = document.querySelector('.main-content');
  input.addEventListener('input', function() {
    var query = this.value.trim().toLowerCase();
    var cards = mainContent.querySelectorAll('.chapter-card');
    if (!query) {
      cards.forEach(function(c) { c.style.display = ''; });
      return;
    }
    cards.forEach(function(card) {
      var txt = card.textContent.toLowerCase();
      card.style.display = txt.includes(query) ? '' : 'none';
    });
  });
})();

// === MathJax Re-render on Details Toggle ===
document.querySelectorAll('details.derive-steps, details.quiz-answer').forEach(function(det) {
  det.addEventListener('toggle', function() {
    if (det.open && window.MathJax && MathJax.typesetPromise) {
      MathJax.typesetPromise([det]).catch(function() {});
    }
  });
});
</script>

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

**图片格式说明**：提取脚本会自动过滤浏览器不兼容的图片格式（EMF/WMF），仅保留 PNG、JPG、GIF、BMP、WebP 等 Web 兼容格式。如果提取文本中出现 `[图片: xxx.emf]` 标记但对应文件不存在，说明该图片已被自动跳过——此时可考虑用 SVG 示意图替代。

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

**图片内嵌（后处理）**：HTML生成完成后，运行 `python embed_images.py <文件名>.html` 将相对路径图片转换为 base64 data URI，生成完全自包含的 HTML 文件，方便分享和打印。

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

### 4.6 图标与交互系统

在HTML中使用以下CSS类对应图标：

| 图标 | CSS类 | 含义 |
|------|-------|------|
| 📌 | `.callout-def` | 核心概念/定义 |
| 🔑 | `.callout-key` | 关键关系/定理 |
| 📐 | `details.derive-steps` | 可折叠完整推导 |
| ✏️ | `.callout-example` | 例题 |
| 💡 | `blockquote` | 直观理解 |
| ⚠️ | `.callout-warn` | 注意事项/易错点 |
| 📝 | `.quiz-section` | 练习测验 |
| 🃏 | `.flashcard` | 术语闪卡（点击翻转） |

交互元素使用规范：

| 交互组件 | HTML模式 | 使用场景 |
|----------|----------|----------|
| 可折叠推导 | `<details class="derive-steps">` | 所有推导步骤，默认折叠 |
| 选项卡视图 | `<div class="tab-container">` | 每章快速复习/详细讲解切换 |
| 练习测验 | `<div class="quiz-section">` | 每章末2-4道概念检查题 |
| 术语闪卡 | `<div class="flashcard-grid">` | 每章3-5张核心术语卡 |
| 进度追踪 | `.section-checkbox` + `.progress-bar-fill` | 侧边栏 ToC checkbox |
| 搜索过滤 | `.search-input` | 主内容区顶部搜索栏 |

### 4.7 质量确保标准

生成文档时逐条自检：

1. **双语精确性**：所有关键技术术语同时给出中文和英文
2. **数学排版**：所有公式使用LaTeX，重要结果 `\boxed{}`
3. **公式完整性**：每个提取出的公式逐一检查，无断裂、无符号丢失
4. **推导补全**：所有被跳过的推导步骤已补全，每步有文字解释
5. **分层解释**：每个核心概念包含 定义→配图→直觉→推导→例题→关联
6. **图文并茂**：每章至少3张课件原图，每个核心概念至少1张示意图
7. **SVG补充**：课件原图不足处，用SVG示意图补充
8. **交互式学习**：每章必须有选项卡视图、可折叠推导、练习测验、术语闪卡
9. **深度脚手架**：可层层深入——frontmatter→第0章→闪卡快览→选项卡切换→精读→测验→附录
10. **多遍阅读设计**：快速复习选项卡→详细讲解选项卡→测验自检→进度追踪
11. **学生同理心**：对比表格、记忆口诀、日常比喻、翻卡记忆
12. **考试实用主义**：关键考点标注、附录B解题模板、附录C常见错误
13. **统一视觉语言**：一致的CSS类、标题层级、表格格式、块引用约定

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
- [ ] 图标系统（📌🔑📐✏️💡📝🃏）使用一致，对应的CSS类正确
- [ ] 每章至少3张课件原图，图片路径正确可访问
- [ ] 核心概念（📌标记）至少配1张示意图（原图或SVG）
- [ ] SVG示意图质量合格：配色一致、标签清晰、语义正确
- [ ] 关键术语均为中英双语
- [ ] 附录A按主题分类，包含课程所有核心公式
- [ ] 附录B至少3种解题模板
- [ ] 附录C至少5条常见错误
- [ ] 各章节标注对应课件来源
- [ ] 目录锚点链接与章节id一一对应
- [ ] MathJax local-first + CDN fallback 引用正确，HTML在浏览器中可正常渲染
- [ ] 已运行 `embed_images.py` 将图片内嵌为 base64（如适用）
- [ ] 移动端和打印样式均可用
- [ ] 每章推导步骤使用 `<details class="derive-steps">` 可折叠
- [ ] 每章有选项卡布局（⚡快速复习 + 📖详细讲解）
- [ ] 每章快速复习面板有3-5张 flashcard 术语闪卡
- [ ] 每章有2-4道练习题的 `.quiz-section`
- [ ] 侧边栏 ToC 有进度追踪 checkbox + 进度条
- [ ] 主内容区顶部有搜索栏
- [ ] 打印时交互元素正确降级（所有内容可见，无控件）
- [ ] JavaScript 为单内联 `<script>` 块，无外部依赖
- [ ] 自主 agent 生成时包含 autonomous-banner（如适用）

---

## Phase 6：考试押题文档（可选）

基于课程内容分析的预测性练习文档，帮助学生在考前针对性查漏补缺。

### 6.1 需求确认时机

| 运行模式 | 何时询问押题需求 |
|----------|------------------|
| **交互式模式** | 在 Phase 1 A3 确认考试范围时**提前询问**，不要等到文档生成后 |
| **自主模式** | 默认不生成，除非 `exam-scope.json` 中明确配置 `generate_prediction: true` |

### 6.2 交互式模式：确认需求（已在 Phase 1 A3 完成）

在 Phase 1 中已询问：
1. 是否需要押题文档？
2. 输出为**单独的 HTML 文件**还是**追加到复习文档末尾**？
3. 考试题型有哪些？（选择题、填空题、简答题、计算题等）
4. 期望的题目数量？

### 6.2 押题分析

在生成押题前，AI 需分析课程内容中的以下信号：

1. **高频概念**：在多个章节/课件中反复出现的概念
2. **重点推导**：课件中有完整推导过程的公式（授课者花了时间讲解）
3. **课件标注**：课件中标记为"重点""掌握""必考"的内容
4. **例题分布**：课件中提供的例题类型和对应的知识点
5. **跨章节主题**：连接多个章节的综合性概念（常出综合题）
6. **套公式题型**：流程化的计算题（常出大题）
7. **概念对比**：容易混淆的概念对（常出简答/辨析题）

### 6.3 押题文档结构

```
1. 押题概述：预测题型分布、各章节出题概率、难度预估
2. 分章节押题（每章）：
   - 🔴 高频考点：[概念] —— 预测理由、可能出题形式
   - 📐 重点推导题：2-4 道完整推导题及详细解答
   - ✏️ 概念应用题：2-3 道简答/计算题及解答
3. 模拟试卷：一份完整的预测试卷
   - 按用户指定的题型结构编排
   - 参考答案与评分要点
4. 附录：押题依据表（每道题 → 对应课件页码/幻灯片）
```

### 6.4 押题文档HTML模板

添加以下CSS变量和样式块到押题文档的 `<style>` 中（押题文档使用独立的极简试卷风格）：

```html
<style>
  /* 试卷风格变量覆盖 */
  :root {
    --primary: #1a1a2e;
    --primary-dark: #0f0f1a;
    --bg: #fafaf9;
    --text: #1a1a2e;
    --font-body: "Songti SC", "SimSun", "Noto Serif CJK SC", serif;
  }

  /* 可折叠解答 */
  details.solution {
    margin: 0.8rem 0;
    padding: 0.8rem 1rem;
    background: #f0f9ff;
    border: 1px dashed #3b82f6;
    border-radius: 8px;
  }
  details.solution summary {
    cursor: pointer;
    font-weight: 600;
    color: #2563eb;
    user-select: none;
  }

  /* 打印时隐藏解答 */
  @media print {
    .no-print-solution details.solution { display: none; }
    body { font-size: 12pt; }
    h1 { font-size: 18pt; }
  }
</style>
```

**答案展示规范**：
- 完整推导过程（不要省略步骤）
- 最终结果用 `\boxed{}` 标注
- 每题后标注**考点来源**（对应课件文件+页码）
- 评分要点（如有分值）
- 常见错误预判

### 6.5 押题原则

1. **基于课件，不臆测**：每个预测必须有对应的课件内容支撑
2. **区分优先级**：用 🔴🟡🟢 标记预测置信度
3. **覆盖重点**：优先覆盖课件中反复强调和完整推导的内容
4. **完整性**：推导题必须提供从起点到结果的完整步骤
5. **不替代复习文档**：押题文档是补充练习，不得省略复习文档中的基础概念讲解
6. **实事求是**：如果课程内容不足以支撑有质量的押题，诚实告知用户

---

## 输出

将生成的HTML保存为用户指定的文件名。如用户请求了押题文档（Phase 6），一并生成。

向用户报告文档统计：章节数、例题数、公式数（近似）、补全的推导数、引用课件图片数、生成SVG数、附录条目数、押题数（如有）。
