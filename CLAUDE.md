# CLAUDE.md

This is the **agent-edu-reviewkit** project — a cross-platform agent skill that converts course materials (PDF/PPTX/DOCX) into a single, self-contained HTML exam-review guide.

## Project structure

```
agent-edu-reviewkit/
├── CLAUDE.md                           # Project instructions (this file)
├── README.md                           # Chinese README (GitHub default)
├── README-en.md                        # English README
├── LICENSE                             # MIT
├── .gitignore                          # Excludes 测试课件(不提交)/ and 测试输出(不提交)/
├── extract_course_materials.py         # Python script: text + image extraction
├── skills/
│   └── course-review-guide.md          # The skill definition (YAML frontmatter)
├── 测试课件(不提交)/                    # Test courseware (NOT committed)
└── 测试输出(不提交)/                    # Test output (NOT committed)
```

## How the skill works

1. **Phase 1 — Scope**: Agent scans courseware files, confirms exam scope with user.
2. **Phase 2 — Extraction**: User runs `extract_course_materials.py` to extract text + images. Agent reads all output. Pure-image files (scan PDFs) are handled via vision fallback.
3. **Phase 3 — Research**: Agent optionally searches GitHub/Wikipedia for supplementary references.
4. **Phase 4 — HTML generation**: Agent produces a single self-contained HTML file with MathJax, inline SVG, extracted images, responsive CSS, and print styles.
5. **Phase 5 — Quality check**: 15-item checklist verification.

## Key conventions

- Output is **HTML**, not Markdown. Math via MathJax 3 CDN.
- SVG diagrams are inline — no external rendering dependencies.
- Extracted images are referenced via relative paths (`extracted_images/xxx.png`).
- The skill is platform-agnostic: works on Claude Code, Copilot, Codex, Kimi Code.
- Image recognition uses a fallback chain: model vision → MCP → user guidance.
- Primary content always comes from user's course materials; web search is supplementary only.
- All formulas use LaTeX; key results use `\boxed{}`.
- Document structure: 8 sections (frontmatter → reading guide → ToC → Ch.0 → chapters → appendices A/B/C).
