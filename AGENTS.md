# Agent 指令

## 项目概述

本项目（agent-edu-reviewkit）是一个跨平台 AI 技能，将课程原始课件（PDF/PPTX/DOCX）转化为图文并茂的高质量交互式 HTML 考试复习文档。输出为单个自包含 HTML 文件，包含 MathJax 数学排版、内联 SVG 示意图、课件原图、完整公式推导、例题详解、交互式学习组件（可折叠推导、选项卡视图、练习测验、术语闪卡、进度追踪）、答题模板和常见错误附录。

## 主要技能

完整技能定义：`skills/course-review-guide/SKILL.md`

请按照该文件中的 6 个 Phase 逐步执行。以下为不同 Agent 平台的特化适配说明。

## Agent 平台兼容性

| 平台 | 优先级 | 配置文件 | 交互模式 | 视觉能力 |
|------|--------|----------|----------|----------|
| Claude Code | P0 | CLAUDE.md | 完整交互 | 原生视觉 + MCP |
| Codex | P0 | 自定义 Prompt | 完整交互 | 有限 |
| OpenCode | P1 | AGENTS.md, opencode.json | 完整交互 | 取决于模型 |
| OpenClaw/Hermes | P2 | AGENTS.md | 自主（有限交互） | 取决于模型 |

---

## OpenCode 适配（P1）

OpenCode 是一款开源、终端优先、模型无关的 AI 编程智能体。以下为 OpenCode 运行本技能时的适配要点：

### 工具映射

| 操作 | Claude Code 写法 | OpenCode 写法 |
|------|-----------------|---------------|
| 扫描课件文件 | `Bash("ls ...")` | 使用 `Glob` 模式扫描，如 `Glob("**/*.pdf")` |
| 读取提取文本 | `Read` 工具 | 同样使用 `Read` 工具 |
| 写入 HTML 文件 | `Write` 工具 | 同样使用 `Write` 工具 |
| 运行 Python 脚本 | `Bash("python ...")` | `Bash("python3 ...")`（优先使用 python3） |
| MCP 视觉工具 | `ListMcpResourcesTool` + MCP | OpenCode 不使用 MCP 资源列表；直接尝试图片读取 |

### 特殊注意

1. **图片识别**：OpenCode 可能不包含 MCP 视觉服务器。碰到纯图片课件时，直接尝试用模型视觉能力读取图片，如不可用则按 skill 文件中的 Level 3 降级策略处理。
2. **用户交互**：OpenCode 支持完整交互式会话，Phase 1 的范围确认步骤按原流程执行，无需跳过。
3. **自定义 Agent**：本项目提供了 `opencode.json` 中的 `course-review` agent 定义，可通过 OpenCode 的 agent 系统直接调用。

---

## 自主模式：OpenClaw / Hermes 适配（P2）

OpenClaw 和 Hermes 是 Claw 类自主化智能体，通过消息应用（WhatsApp、Telegram、Discord、Slack）运行，**不保证回合制用户交互**。以下为自主模式下的 Phase 适配策略。

### 核心原则

- **永远不要等待交互式用户响应** — 使用"检查是否存在"、"推断自"替代"询问用户"
- **推断值一律标记** — 所有自动推断的信息标注 `[自动推断 - 请验证]`
- **渐进式失败** — 部分完成优于完全停止，缺失部分在输出中明确标注

### Phase 1 替代方案：考试范围确定

采用**三级范围确定策略**：

| 级别 | 方法 | 需要交互 | 可靠性 |
|------|------|----------|--------|
| 1 | 读取课件目录中的 `exam-scope.json` | 不需要 | 高 |
| 2 | 从文件名和内容推断范围 | 不需要 | 中 |
| 3 | 通过消息通道请求数据并等待 | 需要（异步） | 高 |

**Level 1 — exam-scope.json 配置文件**

在课件目录中放置 `exam-scope.json`，格式参见项目根目录的 `exam-scope-template.json`。如找到此文件，读取所有配置值作为 Phase 1 的结果，跳过交互确认。

```json
{
  "course_name_zh": "课程名称（如：线性代数、电路分析等）",
  "course_name_en": "Course Name",
  "course_type": "mathematics|physics|circuits|computer|engineering|signals",
  "instructor": "教师姓名",
  "textbook": "教材名称",
  "exam_type": "闭卷",
  "language": "zh",
  "chapters_in_scope": ["第1章", "第2章", "第3章"],
  "chapters_excluded": ["第6章"],
  "output_filename": "课程_期末复习指南.html"
}
```

**course_type 取值说明**：
| 取值 | 对应科目类别 |
|------|-------------|
| `mathematics` | 数学类（微积分、线性代数、概率论、复变函数等） |
| `physics` | 物理类（力学、电磁学、光学、热力学等） |
| `circuits` | 电路电子类（电路分析、模电、数电、信号与系统等） |
| `computer` | 计算机类（数据结构、算法、操作系统、计算机网络等） |
| `engineering` | 工程类（控制理论、机械原理、土木结构等） |
| `signals` | 信号处理类（DSP、通信原理、图像处理等） |

**Level 2 — 自动推断**

若 `exam-scope.json` 不存在：
1. 使用 `Glob` 扫描课件目录中所有 PDF/PPTX/DOCX 文件
2. 从文件名中提取章节编号和主题（如 `chapter1_L1_introduction.pdf` → 第1章 绪论）
3. 假设所有找到的文件都在考试范围内
4. 在生成的 HTML 封面信息中，所有推断值标注 `[自动推断]`
5. 在课件目录中自动生成 `exam-scope-template.json`（含推断的默认值），供用户下次填写

**Level 3 — 异步请求**

通过消息通道发送范围确认请求，等待用户回复后继续。

### Phase 2 替代方案

- 直接运行提取脚本，不暂停请求权限
- 脚本失败则尝试调试并重试一次，仍失败则生成错误报告后停止

### Phase 3 替代方案

- 将补充调研视为**强制**而非可选
- 直接执行搜索，不请求许可

### Phase 4 替代方案

- 使用推断值生成 HTML
- 采用串行 Python 脚本分批追加模式（Write 工具写入头部 → Python 脚本逐批追加2-3章 → 最后追加附录+JS），避免子Agent或一次性生成导致的超时和输出截断
- 在文档顶部（hero 区域之后）插入醒目的自主模式横幅：
  > ⚠ 此文档由自主代理自动生成，考试范围为自动推断，请仔细核对。如需修正，请编辑课件目录中的 `exam-scope.json` 后重新生成。

### Phase 6 替代方案

- 默认生成押题文档（除非 `exam-scope.json` 中另有配置）
- **作为独立 HTML 文件输出**，不追加到复习文档末尾

### 输出信令

完成后，输出结构化摘要：
1. 使用的源文件列表及数量
2. 推断或配置的考试范围
3. 待验证项清单
4. 不完整章节列表（如有）
5. 生成的 `exam-scope-template.json` 路径
