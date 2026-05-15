# CLAUDE.md

This is the **agent-edu-reviewkit** project — a cross-platform agent skill that converts course materials (PDF/PPTX/DOCX) into a single, self-contained interactive HTML exam-review guide.

## Project structure

```
agent-edu-reviewkit/
├── CLAUDE.md                           # Project instructions (this file)
├── AGENTS.md                           # Agent instructions for OpenCode/OpenClaw/Hermes
├── README.md                           # Chinese README (GitHub default)
├── README-en.md                        # English README
├── LICENSE                             # MIT
├── requirements.txt                    # Python dependencies
├── .gitignore                          # Excludes 测试课件(不提交)/ and 测试输出(不提交)/
├── extract_course_materials.py         # Python script: text + image extraction
├── embed_images.py                     # Python script: base64 image embedding
├── setup_mathjax.py                    # Python script: offline MathJax v3 download
├── opencode.json                       # OpenCode custom agent definition
├── exam-scope-template.json            # Template for exam scope config (autonomous agents)
├── skills/
│   ├── course-review-guide.md          # The primary skill definition (YAML frontmatter)
│   └── course-notes.md                 # Chapter-by-chapter notes skill
├── 测试课件(不提交)/                    # Test courseware (NOT committed)
└── 测试输出(不提交)/                    # Test output (NOT committed)
```

## How the skill works

1. **Phase 1 — Scope**: Agent scans courseware files, confirms exam scope with user. Autonomous agents (OpenClaw/Hermes) read `exam-scope.json` or infer scope from filenames.
2. **Phase 2 — Extraction**: User runs `extract_course_materials.py` to extract text + images. Agent reads all output. Pure-image files (scan PDFs) are handled via vision fallback.
3. **Phase 3 — Research**: Agent optionally searches GitHub/Wikipedia for supplementary references.
4. **Phase 4 — HTML generation**: Agent produces a single self-contained interactive HTML file. Built using serial Python script append mode (Write tool for header/CSS → Python scripts for chapter batches → final append for appendices + JS). Sub-agents are prohibited — they fail with large outputs.
5. **Phase 5 — Quality check**: 25-item checklist verification.
6. **Phase 6 — Exam predictions (optional)**: Agent generates a standalone HTML exam prediction document (multiple choice, fill-in-blank, calculation problems). Always output as an independent HTML file — never append to the review document.

## Multi-agent support

| Platform | Priority | Config file | Interaction mode |
|----------|----------|-------------|-----------------|
| Claude Code | P0 | CLAUDE.md | Full interactive |
| Codex | P0 | Custom Prompt | Full interactive |
| OpenCode | P1 | AGENTS.md, opencode.json | Full interactive |
| OpenClaw/Hermes | P2 | AGENTS.md | Autonomous (limited interaction) |

See `AGENTS.md` for platform-specific adaptations.

## Key conventions

- Output is **interactive HTML**, not Markdown. Math via MathJax 3 CDN.
- SVG diagrams are inline — no external rendering dependencies.
- Extracted images are embedded as base64 data URIs via the `embed_images.py` post-processing step, making the HTML fully self-contained.
- The skill is platform-agnostic: works on Claude Code, Copilot, Codex, OpenCode, OpenClaw, Hermes, Kimi Code.
- Image recognition uses a fallback chain: model vision → MCP → user guidance.
- Primary content always comes from user's course materials; web search is supplementary only.
- All formulas use LaTeX; key results use `\boxed{}`.
- Interactive components: collapsible derivations (`<details>`), tabbed views, practice quizzes, flashcard flip cards, progress tracker (localStorage), search/filter.
- Document structure: 8 sections (frontmatter → reading guide → ToC → Ch.0 → chapters → appendices A/B/C).
- Autonomous agents use `exam-scope.json` in courseware directory to preset exam scope without interaction.
