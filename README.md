# agent-edu-reviewkit 🎓

> 一个跨平台的 AI 助手技能（Skill），将课程原始课件（PDF/PPTX/DOCX）一键转化为**图文并茂的交互式 HTML 考试复习文档**。

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/platform-Claude%20Code%20%7C%20OpenCode%20%7C%20Codex%20%7C%20OpenClaw-green)]()
[![Python](https://img.shields.io/badge/python-3.9%2B-blue)]()

[English version](README-en.md)

---

## 目录

- [效果预览](#效果预览)
- [前置准备](#前置准备)
- [快速开始](#快速开始)
- [详细使用说明](#详细使用说明)
- [交互式学习功能](#交互式学习功能)
- [支持平台](#支持平台)
- [自主智能体支持](#自主智能体支持)
- [常见问题](#常见问题)
- [贡献指南](#贡献指南)
- [许可证](#许可证)

---

## 效果预览

输入：一个包含课件 PDF/PPTX/DOCX 的文件夹

输出：一个**自包含交互式 HTML 文件**，包含：
- 📋 考试封面信息（范围、形式、教材）
- 📖 分层阅读指南（适合不同基础的复习路径）
- 📑 可点击的目录导航 + 学习进度追踪
- 🔍 全文搜索功能
- 🗺️ 课程核心思维导图（内联 SVG）
- 📌 核心概念精讲（中英双语，含完整公式推导）
- 🔑 关键定理与关系
- 📐 **可折叠推导步骤**（点击展开，节省页面空间）
- ⚡📖 **选项卡视图**（快速复习/详细讲解切换）
- 🃏 **术语闪卡**（点击翻转，正面术语/背面定义）
- 📝 **练习测验**（概念检查 + 可揭示答案）
- ✏️ 例题详解（题目后紧跟解答，方便对照）
- 💡 通俗直观理解（日常比喻和记忆口诀）
- 🖼️ 课件原图（取自课件内部）+ 内联 SVG 示意图
- 📋 附录 A：公式速查卡
- 📋 附录 B：标准题型解题模板
- 📋 附录 C：常见错误与陷阱
- 🖨️ 打印优化样式

### 示例截图

> 将你的课件放入文件夹，启动技能即可得到类似的复习文档。
> 参考效果见项目内测试课件（DSP 数字信号处理课程，24个PDF）生成的复习文档。

---

## 前置准备

### 1. 安装 AI 编程助手

选择以下任一 AI 编程助手并完成安装：

| 助手 | 安装方式 | 交互模式 |
|------|---------|----------|
| **Claude Code** | [官方安装指南](https://docs.anthropic.com/en/docs/claude-code) | 完整交互 |
| **OpenCode** | `npm install -g opencode-ai` | 完整交互 |
| **OpenAI Codex CLI** | `npm install -g @openai/codex` | 完整交互 |
| **GitHub Copilot** | [VS Code 扩展](https://marketplace.visualstudio.com/items?itemName=GitHub.copilot) | 完整交互 |
| **Kimi Code** | [官方文档](https://kimi.moonshot.cn/) | 完整交互 |
| **OpenClaw/Hermes** | [安装文档](https://docs.openclaw.ai/) | 自主模式 |

### 2. 安装 Python（3.9 或以上版本）

- **Windows**: 从 [python.org](https://www.python.org/downloads/) 下载安装包，安装时勾选"Add Python to PATH"
- **macOS**: `brew install python@3`
- **Linux (Ubuntu/Debian)**: `sudo apt install python3 python3-pip`
- **Linux (Fedora)**: `sudo dnf install python3 python3-pip`

验证安装：

```bash
python --version   # 应显示 Python 3.9 或以上
pip --version
```

### 3. 安装 Python 依赖

```bash
pip install pypdf python-pptx python-docx
```

这三个库均无 C 编译依赖，直接 pip 安装即可，无需安装 Visual Studio Build Tools 等额外工具。

---

## 快速开始

### 1. 克隆项目

```bash
git clone https://github.com/lijiawei255/agent-edu-reviewkit.git
cd agent-edu-reviewkit
```

### 2. 准备课件

将你的课件文件（`.pdf`、`.pptx`、`.docx` 及其变体）放入一个文件夹中，例如：

```
./我的课件/
    ├── 第1章_引言.pdf
    ├── 第2章_基础理论.pptx
    ├── 第3章_应用.docx
    └── ...
```

### 3. 在 AI 助手中调用技能

**Claude Code 用户**：

由于技能文件 `skills/course-review-guide.md` 已包含在项目中，直接向 Claude Code 说：

```
请帮我整理课程复习文档
```

Claude Code 会自动检测并加载技能。你也可以手动触发：

```
/技能:course-review-guide
```

> 注意：请确保在项目目录（`agent-edu-reviewkit/`）中启动 Claude Code，或使用 `--skills` 参数指向本项目的 `skills/` 目录。

**OpenCode 用户**：

项目根目录已包含 `opencode.json` 配置文件，其中定义了 `course-review` 自定义 agent。启动 OpenCode 后：

```
# 连接到你的模型提供商后
@course-review 帮我生成复习文档，课件在 [目录路径]
```

> 适配详情见项目根目录的 `AGENTS.md`。

**其他 AI 助手用户**：

将 `skills/course-review-guide.md` 的内容作为系统提示（System Prompt）或自定义指令（Custom Instructions）加载到你的 AI 助手中。

**通用方式（适用于所有平台）**：

直接向 AI 助手发送以下内容：

```
请按照 skills/course-review-guide.md 中的指引，
帮我把 [课件目录路径] 中的课件转化为HTML考试复习文档。
```

### 4. 跟随指引完成

AI 助手会依次引导你：
1. 确认课件目录和考试范围
2. 运行提取脚本（`extract_course_materials.py`）
3. 生成交互式 HTML 复习文档
4. 运行图片内嵌脚本（`embed_images.py`）获得自包含 HTML
5. （可选）生成考试押题文档

最终输出为一个自包含的 `.html` 文件，用浏览器打开即可阅读和打印。

---

## 详细使用说明

### 工作流程

整个流程分为六个阶段：

```
课件文件 ──→  Phase 1: 范围确认  ──→  Phase 2: 内容提取  ──→  Phase 3: 补充调研
                                                                        │
                                                                        ▼
                          HTML复习文档  ←──  Phase 5: 质量检查  ←──  Phase 4: HTML生成
                                                                        │
                                                                        ▼
                                                            Phase 6: 考试押题（可选）
```

### Phase 1：范围确认

AI 助手会扫描课件目录，列出所有文件，并与你确认：
- 考试范围（哪些章节考、哪些不考）
- 课程名称、教师、教材
- 考试形式（闭卷/开卷）
- 输出文件名

**建议**：提前准备一份考点清单或范围说明（文字或截图均可），直接提供给 AI 助手。

### Phase 2：内容提取

AI 助手会引导你运行 `extract_course_materials.py` 脚本：

```bash
# 1. 编辑脚本中的配置区（第49-53行），修改为你的实际路径
# 课件目录 = r"你的课件目录路径"
# 文本输出目录 = r"extracted_text"
# 图片输出目录 = r"extracted_images"

# 2. 运行脚本
python extract_course_materials.py
```

脚本会自动：
- 提取所有课件的文本和图片
- 检测纯图片型课件（扫描版PDF等）并单独标注
- 在文本中用 `[图片: xxx.png]` 标记图片位置
- 输出提取报告
- 检测 `exam-scope.json`（如有），输出考试范围配置

### Phase 3：补充调研（可选）

AI 助手会搜索以下来源补充对课程内容的理解：
- GitHub 上的开源课程笔记和习题解答
- Wikipedia 上的权威概念定义
- 相关学术教程

**所有外部内容仅作为参考**，最终以你提供的课件为准。

### Phase 4：HTML 生成

AI 助手基于全部课件内容生成单文件**交互式** HTML 复习文档，包括：
- **MathJax** 渲染的数学公式（LaTeX 格式）
- **内联 SVG** 示意图（流程图、对比图、坐标图等）
- **课件原图**（生成时使用相对路径，后通过 `embed_images.py` 内嵌为 base64）
- **CSS 样式**（响应式设计 + 打印样式 + 宽屏侧边目录）
- **交互式组件**（可折叠推导、选项卡、闪卡、测验、进度追踪、搜索）
- **内联 JavaScript**（无外部依赖，单文件自包含）

生成后运行 `python embed_images.py <文件名>.html` 将图片全部内嵌，获得完全自包含的 HTML 文件。

### Phase 5：质量检查

AI 助手自动进行 25 项质量检查，确保输出完整可用。检查项涵盖结构完整性、交互功能、数学排版、打印兼容等。

### Phase 6：考试押题（可选）

完成复习文档后，AI 助手可基于课程内容分析生成一份**考试押题文档**——包含高频考点预测、分章节练习题、模拟试卷及答案解析，帮助学生考前针对性查漏补缺。

### 图片识别能力

对于纯图片型课件（扫描版 PDF、纯图片 PPTX），本技能采用**三级降级策略**：

| 优先级 | 方案 | 说明 |
|--------|------|------|
| 1 | AI 模型自带视觉 | 直接读取图片内容（需要支持多模态的模型，如 Claude Opus 4、GPT-4V、Gemini Pro Vision） |
| 2 | MCP 视觉服务器 | 通过 MCP 协议调用视觉工具（如 MiniMax MCP） |
| 3 | 引导用户处理 | 引导用户切换模型、安装 MCP 或使用本地 OCR（Tesseract） |

如果你使用的 AI 助手不支持图片识别，请切换到支持视觉的模型或安装 MCP 视觉服务器。

### 适用课程类型

本技能专为**理工科课程考试复习**设计，特别适合：

- **数学密集型课程**：高等数学、线性代数、概率论、复变函数
- **信号/系统类课程**：数字信号处理、信号与系统、通信原理
- **物理/力学课程**：大学物理、理论力学、量子力学
- **编程/算法课程**：数据结构、算法设计、机器学习

对于概念记忆型课程（如生物、历史、医学），同样适用——技能会自动调整策略，增加对比表格、记忆口诀和思维导图。

---

## 交互式学习功能

生成的 HTML 复习文档包含以下交互式学习组件，参考自 [Thariq 的《Using Claude Code: The Unreasonable Effectiveness of HTML》](https://x.com/thariqk) 中关于 HTML 交互性的建议：

### 可折叠推导步骤

所有数学推导默认折叠，点击展开。节省页面空间，适合学生按需查看详解。打印时自动展开所有内容。

### 选项卡视图

每章包含两个选项卡：
- **⚡ 快速复习**：章节概要、术语闪卡、关键公式表格
- **📖 详细讲解**：完整推导、例题详解、配图说明

### 术语闪卡（Flashcard）

核心术语的翻转闪卡——正面显示术语名称，点击翻转显示定义或公式。利用 CSS 3D 翻转效果，支持鼠标和触控。

### 练习测验

每章末有 2-4 道概念检查题，答案默认隐藏，点击"显示答案"查看解析。适合自我检测掌握程度。

### 学习进度追踪

侧边栏目录包含 checkbox，勾选已完成的章节，顶部进度条实时更新。进度保存在浏览器 localStorage 中，刷新页面不丢失。

### 全文搜索

文档顶部的搜索栏支持按关键词过滤章节，快速定位需要的概念或公式。

### 打印兼容

打印时，所有交互元素自动降级：折叠内容展开、所有选项卡显示、闪卡展开为正面+背面、隐藏搜索和进度控件。

---

## 支持平台

| 平台 | 优先级 | 配置文件 | 交互模式 |
|------|--------|----------|----------|
| **Claude Code** | P0 | `CLAUDE.md` | 完整交互 |
| **OpenAI Codex CLI** | P0 | 自定义 Prompt | 完整交互 |
| **OpenCode** | P1 | `AGENTS.md`, `opencode.json` | 完整交互 |
| **OpenClaw/Hermes** | P2 | `AGENTS.md` | 自主模式 |
| **GitHub Copilot** | — | `.github/copilot-instructions.md` | 完整交互 |
| **Kimi Code** | — | 自定义指令 | 完整交互 |
| **Cursor** | — | `.cursor/rules/` | 完整交互 |

平台适配细节见 `AGENTS.md`。

---

## 自主智能体支持

OpenClaw、Hermes 等 Claw 类自主智能体以全自动方式运行，**不保证回合制用户交互**。本技能针对自主模式做了专门适配。

### exam-scope.json 配置文件

在课件目录中放置 `exam-scope.json`，自主 agent 会自动读取并跳过交互式范围确认：

```json
{
  "course_name_zh": "数字信号处理",
  "course_name_en": "Digital Signal Processing",
  "instructor": "张三",
  "textbook": "《数字信号处理》，程佩青，第四版",
  "exam_type": "闭卷",
  "language": "zh",
  "chapters_in_scope": ["第1章", "第2章", "第3章", "第4章", "第5章"],
  "chapters_excluded": ["第6章"],
  "output_filename": "DSP_期末复习指南.html"
}
```

项目根目录的 `exam-scope-template.json` 提供了完整的字段模板。

### 三级范围确定策略

| 级别 | 方法 | 需要交互 | 可靠性 |
|------|------|----------|--------|
| 1 | 读取 `exam-scope.json` | 不需要 | 高 |
| 2 | 从文件名和内容推断范围 | 不需要 | 中 |
| 3 | 通过消息通道请求 | 需要（异步） | 高 |

### 自动推断模式

如果 `exam-scope.json` 不存在，自主 agent 会从课件文件名推断章节范围，生成的 HTML 文档顶部会显示醒目的**自主模式横幅**，提醒用户核对考试范围。同时会在课件目录自动生成 `exam-scope-template.json`（含推断的默认值），供用户下次填写以获得更精确的结果。

详细适配说明见 `AGENTS.md`。

---

## 常见问题

### Q: 我的课件是扫描版 PDF（纯图片），没有任何文字，怎么办？

如果扫描质量较好，AI 助手的视觉能力可以直接识别图片中的内容。如果当前模型不支持视觉：
1. 切换到支持多模态的模型（Claude Opus 4、GPT-4V 等）
2. 安装 MCP 视觉服务器
3. 使用 OCR 工具（如 Tesseract）先转换为文本

### Q: 公式提取后不完整或显示为乱码？

PDF 文本提取可能导致公式损坏。本技能会自动检测并修复 6 类常见公式问题（断裂、符号丢失、分数线丢失、上下标错位、矩阵混乱、函数名错误）。所有公式均以 LaTeX 格式重新排版，确保在 HTML 中正确渲染。

### Q: 生成的 HTML 文件太大怎么办？

HTML 的 CSS 和内联 SVG 占用空间有限。运行 `embed_images.py` 将图片内嵌为 base64 后，文件会增大（约为原始图片总大小的 1.37 倍），但换来的是完全自包含、可单文件分享的便利。如果文件太大，也可以不运行内嵌脚本，改为将 HTML 与 `extracted_images/` 文件夹一起打包分享。

### Q: 如何分享和打印复习文档？

- **分享**：运行 `python embed_images.py <文件名>.html` 得到 `_embedded.html` 文件，图片全部内嵌其中，单文件即可分享
- **打印**：在浏览器中打开 HTML，按 `Ctrl+P`（或 `Cmd+P`）。内置的 `@media print` 样式会自动优化排版，所有折叠内容自动展开

### Q: 交互功能（闪卡、测验等）需要联网吗？

不需要。所有交互功能使用纯 HTML/CSS/JavaScript 实现，无外部 JS 依赖。唯一需要联网的是 MathJax 公式渲染（离线方案见下方）。

### Q: 学习进度会丢失吗？

进度保存在浏览器的 localStorage 中，刷新页面不会丢失。注意：进度与文件路径绑定，如果移动文件位置，进度会重置。

### Q: 支持哪些课件格式？

| 格式 | 扩展名 | 支持状态 |
|------|--------|---------|
| PDF | `.pdf` | ✅ 完全支持 |
| PowerPoint | `.pptx`, `.pptm` | ✅ 完全支持 |
| Word | `.docx`, `.dotx`, `.dotm` | ✅ 完全支持 |
| 旧版 PowerPoint | `.ppt` | ❌ 不支持，请先用 PowerPoint 另存为 `.pptx` |
| 旧版 Word | `.doc` | ❌ 不支持，请先用 Word 另存为 `.docx` |

### Q: 如何在无网络环境下查看公式？

生成的 HTML 依赖 MathJax CDN 加载公式渲染脚本，需要联网。无网络环境下有两种方案：
1. **浏览器打印/另存为PDF**：在有网络时先用浏览器的"打印 → 另存为PDF"功能保存
2. **下载 MathJax 本地部署**：从 [MathJax GitHub](https://github.com/mathjax/MathJax) 下载完整包，解压到 HTML 同级目录下的 `mathjax/` 文件夹，然后将 HTML 中 MathJax `<script>` 的 `src` 改为 `./mathjax/es5/tex-svg.js`

### Q: 我的课件是英文授课的，能用吗？

可以。本技能支持中英双语授课——关键术语会同时给出中英文对照。如果是全英文授课，请在与 AI 助手确认范围时说明。

### Q: 如何用 OpenClaw/Hermes 自主生成复习文档？

1. 在课件目录中创建 `exam-scope.json`（参考 `exam-scope-template.json` 填写考试信息）
2. 将项目克隆到 OpenClaw 可访问的位置
3. OpenClaw agent 会读取 `AGENTS.md` 中的指令，自动执行所有 Phase
4. 生成完成后检查文档顶部的自主模式横幅，确认考试范围正确

---

## 贡献指南

欢迎对本项目做出贡献！以下是如何参与：

### 提交 Issue

如果你：
- 发现了 Bug
- 有功能建议
- 希望支持新的课件格式或 AI 平台
- 有使用问题

请在 [GitHub Issues](https://github.com/lijiawei255/agent-edu-reviewkit/issues) 提交。

### 提交 Pull Request

1. **Fork** 本仓库
2. 创建你的特性分支：`git checkout -b feature/amazing-feature`
3. 提交你的修改：`git commit -m 'feat: add amazing feature'`
4. 推送到分支：`git push origin feature/amazing-feature`
5. 打开 Pull Request

**提交前请检查**：
- [ ] 修改与现有代码风格一致
- [ ] `extract_course_materials.py` 在 Python 3.9+ 下测试通过
- [ ] 新功能有适当的文档说明
- [ ] 不包含测试课件或测试输出文件（这些文件已在 `.gitignore` 中排除）

### 本地开发

```bash
# 克隆项目
git clone https://github.com/lijiawei255/agent-edu-reviewkit.git
cd agent-edu-reviewkit

# 安装依赖
pip install pypdf python-pptx python-docx

# 测试课件和输出目录由 .gitignore 自动排除
# 将测试课件放入 测试课件(不提交)/ 目录
```

---

## 许可证

本项目基于 MIT 许可证发布。详见 [LICENSE](LICENSE) 文件。

Copyright (c) 2026 Jiawei Li
