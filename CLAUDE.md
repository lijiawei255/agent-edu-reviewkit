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
│   ├── course-review-guide.md          # Main orchestrator skill (slimmed, references sub-skills)
│   ├── course-notes.md                 # Chapter-by-chapter notes skill
│   ├── extraction-rules-science.md     # Science/engineering extraction rules (formulas, derivations, code)
│   ├── extraction-rules-humanities.md  # Humanities/social-science extraction rules (concepts, timelines, essays)
│   ├── example-handling.md             # Example extraction, solution walkthrough, variant problems
│   └── output-generation.md            # HTML + PDF dual-format output, Chinese font/P encoding
├── 测试课件(不提交)/                    # Test courseware (NOT committed)
└── 测试输出(不提交)/                    # Test output (NOT committed)
```

## How the skill works

1. **Phase 1 — Scope**: Agent scans courseware files, confirms exam scope with user. Autonomous agents read `exam-scope.json` or infer scope from filenames.
2. **Phase 2 — Extraction + Classification**: User runs `extract_course_materials.py` to extract text + images. Agent reads all output, classifies each chapter as science/humanities/mixed, and **identifies all examples** in the courseware.
3. **Phase 3 — Research**: Agent optionally searches GitHub/Wikipedia for supplementary references.
4. **Phase 4 — HTML+PDF generation**: Agent produces a single self-contained interactive HTML file and converts it to PDF via weasyprint. Uses serial Python script append mode — sub-agents are prohibited.
5. **Phase 5 — Quality check**: Dual-format checklist (HTML rendering + PDF encoding/formulas).
6. **Phase 6 — Exam predictions (optional)**: Standalone exam prediction document (HTML+PDF).

## Multi-agent support

| Platform | Priority | Config file | Interaction mode |
|----------|----------|-------------|-----------------|
| Claude Code | P0 | CLAUDE.md | Full interactive |
| Codex | P0 | Custom Prompt | Full interactive |
| OpenCode | P1 | AGENTS.md, opencode.json | Full interactive |
| OpenClaw/Hermes | P2 | AGENTS.md | Autonomous (limited interaction) |

See `AGENTS.md` for platform-specific adaptations.

## Key conventions

- **Output is dual-format: HTML + PDF**. HTML for interactive study, PDF for printing. Both generated from the same source. PDF via weasyprint with explicit Chinese font configuration.
- Math via MathJax 3 CDN (local-first + CDN fallback).
- SVG diagrams are inline — no external rendering dependencies.
- Extracted images are **strictly filtered**: logos, decorations, repeated images, and EMF/WMF formats are discarded. Only formula diagrams, concept illustrations, and structure charts are kept. Each retained image must correspond to a specific formula or concept.
- Images are embedded as base64 data URIs via `embed_images.py` post-processing.
- **Courseware examples are mandatory**: every example in the slides must be extracted with full solution walkthrough (WHY each step, not just WHAT) and "举一反三" variant problems.
- The skill is platform-agnostic: Claude Code, Copilot, Codex, OpenCode, OpenClaw, Hermes, Kimi Code.
- Image recognition: model vision → MCP → user guidance.
- Primary content from course materials; web search is supplementary only.
- All formulas use LaTeX; key results use `\boxed{}`.
- Interactive components: collapsible derivations (`<details>`), tabbed views, practice quizzes, flashcard flip cards, progress tracker (localStorage), search/filter.
- Document structure: 8 sections (frontmatter → reading guide → ToC → Ch.0 → chapters → appendices A/B/C).
- Science vs humanities content is auto-detected per chapter; both modes can coexist in one document.
- Autonomous agents use `exam-scope.json` to preset exam scope.

## Skill file architecture

The skill is split into focused sub-skills for maintainability:

| File | Role |
|------|------|
| `course-review-guide.md` | Main orchestrator — flow, phases, mode detection |
| `extraction-rules-science.md` | Science/engineering: formula-image correspondence, derivation completion, code handling |
| `extraction-rules-humanities.md` | Humanities: concept comparison tables, timelines, essay frameworks |
| `example-handling.md` | Mandatory example extraction, deep solution walkthroughs, variant problem generation |
| `output-generation.md` | HTML+PDF dual output, Chinese font/encoding, weasyprint configuration |
| `course-notes.md` | Independent chapter-by-chapter notes skill (not exam-focused) |
